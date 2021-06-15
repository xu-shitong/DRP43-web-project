import itertools
from posixpath import abspath
from flask.helpers import url_for

from sqlalchemy import sql
from flask_blog.db import Account, HistoryNode, Note
from html import entities
import re
from flask import (Blueprint, flash, request, session, url_for)
from flask.templating import render_template
from werkzeug.utils import redirect
from flask_blog.app import db
from flask_blog.utils import fetchNote, getNoteInfo, get_my_note
from flask_blog.auth import login_required
from flask_blog.db import PicAndName
import json

bp = Blueprint("edit_page", __name__)

# fetch note data from database, render edit page
def rerender_edit_page(id):
    note = fetchNote(noteId=id, is_in_main=False)

    # tree = itertools.chain.from_iterable()
    return render_template("edit_page.html", note=json.dumps(note), note_id=id, note_name=session["note_name"])


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

    return render_template("edit_page.html", note=json.dumps(note), note_id=id, note_name=session["note_name"], read=session["is_public"][0], write=session["is_public"][1], 
                           base_note=get_my_note(session))



@bp.route("/editNote", methods=["POST"])
@login_required
def change_note_name():
    new_name = request.form["new_note_name"]
    read = request.form["read"]
    write = request.form["write"]
    isPublic = read + write
    note_id = session["note_id"]
    sql_query = f'UPDATE note SET note_name="{new_name}", is_public="{isPublic}" ' \
                f"WHERE id = '{note_id}'"

    db.session.execute(sql_query)
    db.session.commit()

    sql_query_2 = f'SELECT id FROM note WHERE note_name = "{new_name}"'
    (id,) = db.session.execute(sql_query_2).fetchone()
    session['note_name'] = new_name
    # TODO: change here
    # print(url_for("edit_page.edit_page", id=id))
    # return rerender_edit_page(id)
    return redirect(url_for("edit_page.edit_page", id=note_id))


# respond to submit of edit page's update
@bp.route("/update_event", methods=["POST"])
@login_required
def submit_note():
    node_id = request.form["node_id"]
    user_id = session["user_id"]

    # check if user has permission to edit the note
    sql_query = f'SELECT id, is_public, author_id '\
                f'FROM note '\
                f'WHERE id = {session["note_id"]}'
    note = db.session.execute(sql_query).fetchone()
    # TODO: index 1 here indicate priority for other user
    if (not user_id == note["author_id"]) and (note["is_public"][1] == "0"):
        flash("you cannot edit this note, report how you enter this website")
        url = url_for("edit_page.edit_page", id=session["note_id"])
        return redirect(url)

    startTime = int(request.form["start"])
    endTime_temp = request.form["end"]
    if endTime_temp == '':
        endTime = startTime
    else:
        endTime = int(endTime_temp)
    
    if endTime < startTime:
        flash("invalid end time, should be at least equal to start time")
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

    if node_id:
      sql_query = f"DELETE FROM history_node WHERE id={node_id}"
      db.session.execute(sql_query)
      db.session.commit()

      # if deleted a parent node, all immediate child of node become child of root node
      sql_query = 'UPDATE history_node ' \
                  'SET parent_node_id="0" ' \
                  f'WHERE parent_node_id="{node_id}"'
      succeed = db.session.execute(sql_query)
      db.session.commit()
      print(succeed)
      if succeed:
        flash("deleted a parent node, all child moved to root")
    else:
      flash("you didn't select a node to delete")

    url = url_for("edit_page.edit_page", id=session["note_id"])
    return redirect(url)

# respond to delete of a note
@bp.route("/delete_note", methods=["POST"])
def delete_note():
    # verify note is owned by user, only owner of note can delete note
    owner = Note.query.filter_by(id=session['note_id']).first()
    print(owner)
    print(session)
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
