import functools
import itertools
from posixpath import abspath
from flask.helpers import url_for

from sqlalchemy import sql
from flask_blog.db import Account, HistoryNode, InviteRecord, Note
from html import entities
import re
from flask import (Blueprint, g, flash, request, session, url_for)
from flask.templating import render_template
from werkzeug.utils import redirect
from flask_blog.app import db
from flask_blog.utils import fetchNote, getNoteInfo, get_my_note, get_note_with_publicity, is_invited_user
from flask_blog.auth import login_required
from flask_blog.db import PicAndName
import json

bp = Blueprint("edit_page", __name__)

# check if user has permission to edit the note
def check_edit_priviledge():
    # ensure user has logged in
    if not "user_id" in session:
      return False
    
    user_id = session["user_id"]
    sql_query = f'SELECT id, is_public, author_id '\
                f'FROM note '\
                f'WHERE id = {session["note_id"]}'
    note = db.session.execute(sql_query).fetchone()
    # TODO: index 1 here indicate priority for other user
    url = None
    if (not user_id == note["author_id"]) and (not note["is_public"][1] == "2") and (not is_invited_user(user_id, note["id"])):
        flash("you cannot edit this note, report how you enter this website", "warning")
        url = url_for("edit_page.edit_page", id=session["note_id"])
          
    return url

# on enter edit page, id is note_id
@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_page(id):
    session["note_id"] = id
    note_info = getNoteInfo(id)

    if note_info:
      # if successfully fetched note, set session note name
      session["note_name"] = note_info["note_name"]
      session["is_public"] = note_info["is_public"]
    else:
      # if user give bad note id, set note name to None
      return render_template("error/404.html", message=f"note with id: {id} not found")
    
    # fetch note data from database, render edit page
    note = fetchNote(noteId=id, is_in_main=False)

    # fetch all cooperators' user name
    sql_query = "SELECT username FROM account JOIN invite_record ON invited_user_id = account.id"
    cooperators = db.session.execute(sql_query).fetchall()

    return render_template("edit_page.html", note=json.dumps(note), note_id=id, note_name=session["note_name"], read=session["is_public"][0], write=session["is_public"][1], 
                           base_note=get_my_note(session), is_owner=(session["user_id"]==note_info["author_id"]), cooperators=cooperators)



@bp.route("/editNote", methods=["POST"])
@login_required
def change_note_name():
    new_name = request.form["new_note_name"]
    read = request.form["read"]
    write = request.form["write"]
    if read < write:
        # check read publicity higher or equal to write publicity
        flash("change publicity failed, read publicity cannot be lower than write publicity", "warning")
        return redirect(url_for("edit_page.edit_page", id=session["note_id"]))

    isPublic = read + write
    sql_query = f"SELECT * FROM invite_record WHERE note_id = {session['note_id']}"
    publicity = db.session.execute(sql_query).fetchone()
    if publicity and (read < '1' or write < '1'):
        # note was shared with other user, flash user that note will not be shared anymore
        flash("publicity changed to private, note no longer shared", "warning")

    note_id = session["note_id"]
    sql_query = f'UPDATE note SET note_name="{new_name}", is_public="{isPublic}" ' \
                f"WHERE id = '{note_id}'"

    db.session.execute(sql_query)
    db.session.commit()

    sql_query_2 = f'SELECT id FROM note WHERE note_name = "{new_name}"'
    (id,) = db.session.execute(sql_query_2).fetchone()
    session['note_name'] = new_name

    flash("publicity successfully updated!", "success")
    return redirect(url_for("edit_page.edit_page", id=note_id))


# respond to update of edit page's update
@bp.route("/update_event", methods=["POST"])
@login_required
def update_event():
    node_id = request.form["node_id"]
    user_id = session["user_id"]

    url = check_edit_priviledge()
    if url:
        return redirect(url)

    startTime = int(request.form["start"])
    endTime_temp = request.form["end"]
    if endTime_temp == '':
        endTime = startTime
    else:
        endTime = int(endTime_temp)
    
    if endTime < startTime:
        flash("invalid end time, should be at least equal to start time", "warning")
        url = url_for("edit_page.edit_page", id=session["note_id"])
        return redirect(url)

    title = request.form["title"]
    parent_id = request.form.get("parent")

    description = request.form["body"]

    img = request.files.get("pic")

    if node_id:
      # node id present, user is updating a node
      # update database
      sql_query = f'UPDATE history_node ' \
                  f'SET title="{title}", ' \
                  f'start_date="{startTime}", ' \
                  f'end_date="{endTime}", ' \
                  f'content="{description}", ' \
                  f'parent_node_id="{parent_id}" ' \
                  f'WHERE id = {node_id}'
      db.session.execute(sql_query)
      db.session.commit()
    else:
      # node id not present, user is adding a node
      blog = HistoryNode(note_id=session["note_id"], title=title, start_date=startTime, end_date=endTime, content=description, parent_node_id=parent_id)
      db.session.add(blog)
      db.session.commit()

      # get id of new node, in case id is required to upload image
      sql_query = "SELECT LAST_INSERT_ID()"
      note = db.session.execute(sql_query).fetchone()
      node_id = note["LAST_INSERT_ID()"]

    if img:
      # if containing uploaded picture, upload to database
      pic_name = request.form["pic_name"]
      file_path = "../pics/" + str(session["user_id"]) + "_" + img.filename
      pic_and_name = PicAndName(node_id=node_id, name=pic_name, path=file_path)
      db.session.add(pic_and_name)
      db.session.commit()
      img.save(file_path)

    url = url_for("edit_page.edit_page", id=session["note_id"])
    return redirect(url)

@bp.route("/delete_event", methods=["POST"])
def delete_event():
    node_id = request.form["node_id"]

    url = check_edit_priviledge()
    if url :
      return redirect(url)

    if node_id:
      sql_query = f"DELETE FROM history_node WHERE id={node_id}"
      db.session.execute(sql_query)
      db.session.commit()

      # if deleted a parent node, all immediate child of node become child of root node
      sql_query = 'UPDATE history_node ' \
                  'SET parent_node_id="0" ' \
                  f'WHERE parent_node_id="{node_id}"'
      db.session.execute(sql_query)
      db.session.commit()
    else:
      flash("you didn't select a node to delete", "warning")

    url = url_for("edit_page.edit_page", id=session["note_id"])
    return redirect(url)

# respond to delete of a note
@bp.route("/delete_note", methods=["POST"])
def delete_note():
    # verify note is owned by user, only owner of note can delete note
    owner = Note.query.filter_by(id=session['note_id']).first()
    if not (session["user_id"] == owner.author_id):
      # cannot delete note
      return "you are not owner of the note, only creater of note can delete it"

    sql_query = f"DELETE FROM history_node WHERE note_id={session['note_id']}"
    db.session.execute(sql_query)
    db.session.commit()
    sql_query = f"DELETE FROM note WHERE id={session['note_id']}"
    db.session.execute(sql_query)
    db.session.commit()

    # return no error message
    return ""

@bp.route("/invite_user", methods=["POST"])
def invite_user():
    invited_user_id = request.form["invited_user_id"]

    if int(invited_user_id) == session["user_id"]:
        # check user didn't invite himself as new editor
        flash("you cannot invite yourself as editor", "warning")
        return redirect(url_for("edit_page.edit_page", id=session["note_id"]))

    sql_query = "SELECT * FROM invite_record "\
               f"WHERE invited_user_id = {invited_user_id} AND note_id = {session['note_id']}" 
    prevRecord = db.session.execute(sql_query).fetchone()
    if prevRecord:
        # check user did not invite an editor again
        flash("user has already been invited", "warning")
        return redirect(url_for("edit_page.edit_page", id=session["note_id"]))

    note = getNoteInfo(session["note_id"])
    if note["is_public"][1] == '0' or note["is_public"][0] == '0':
        # write or read publicity is private
        flash("read or write publicity is private, cannot invite user edit private note", "warning")
        return redirect(url_for("edit_page.edit_page", id=session["note_id"]))

    sql_query = f"SELECT * FROM account WHERE id = {invited_user_id}"
    invited_user = db.session.execute(sql_query).fetchone()
    if not invited_user:
        # invited user does not exist
        flash(f"no user with id {invited_user_id}, invite failed", "warning")
        return redirect(url_for("edit_page.edit_page", id=session["note_id"]))
    
    invite_record = InviteRecord(invited_user_id=invited_user_id, note_id=session["note_id"])
    db.session.add(invite_record)
    db.session.commit()
    flash("invited cooperator successfully!", "success")
    return redirect(url_for("edit_page.edit_page", id=session["note_id"]))
