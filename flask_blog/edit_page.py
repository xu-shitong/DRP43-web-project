import itertools
from flask.helpers import url_for

from sqlalchemy import sql
from flask_blog.db import Account, HistoryNode, Note
from html import entities
import re
from flask import (Blueprint, flash, request, session)
from flask.templating import render_template
from werkzeug.utils import redirect
from flask_blog.app import db
from flask_blog.utils import dbDummyInit, fetchNote, getNoteInfo
from flask_blog.auth import login_required
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

    # if user give bad note id, set note name to None
    session["note_name"] = None
    if note_info:
      # if successfully fetched note, set session note name
      session["note_name"] = note_info["note_name"]
    
    # fetch note data from database, render edit page
    note = fetchNote(noteId=id, is_in_main=False)

    # tree = itertools.chain.from_iterable()
    return render_template("edit_page.html", note=json.dumps(note), note_id=id, note_name=session["note_name"])

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
    if (not user_id == note["author_id"]) and (note["is_public"] == 0):
        flash("you cannot edit this note, report how you enter this website")
        url = url_for("edit_page.edit_page", id=session["note_id"])
        return redirect(url)

    startTime = int(request.form["start"])
    endTime_temp = request.form["end"]
    if endTime_temp == None:
        endTime = None
    else:
        endTime = int(endTime_temp)

    title = request.form["title"]
    parent_id = request.form.get("parent")

    description = request.form["body"]

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

    else :
      # node id not present, user is adding a node
      blog = HistoryNode(note_id=session["note_id"], title=title, start_date=startTime, end_date=endTime, content=description, parent_node_id=parent_id)
      db.session.add(blog)

    db.session.commit()

    url = url_for("edit_page.edit_page", id=session["note_id"])
    return redirect(url)

@bp.route("/delete_event", methods=["POST"])
def delete_event():
    node_id = request.form["node_id"]
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
