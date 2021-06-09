import itertools
from flask_blog.db import Account, HistoryNode, Note
from html import entities
import re
from flask import (Blueprint, flash, request, session)
from flask.templating import render_template
from werkzeug.utils import redirect
from flask_blog.app import db
from flask_blog.utils import dbDummyInit, fetchNote, getNoteInfo
import json

bp = Blueprint("edit_page", __name__)

# fetch note data from database, render edit page
def rerender_edit_page(id):
    note = fetchNote(noteId=id, is_in_main=False)
    summary = itertools.chain.from_iterable(note["nodes"])
    return render_template("edit_page.html", note=json.dumps(note), summary=summary, note_id=id, note_name=session["note_name"])


# on enter edit page, id is note_id
@bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_page(id):
    session.clear()
    session["note_id"] = id
    note_info = getNoteInfo(id)

    # if user give bad note id, set note name to None
    session["note_name"] = None
    if note_info:
      # if successfully fetched note, set session note name
      session["note_name"] = note_info["note_name"]
    

    # # Dummy initialisation of database, only for test purpose
    # dbDummyInit()

    return rerender_edit_page(id)

# respond to submit of edit page's update
@bp.route("/edit", methods=["POST"])
def submit_note():
    startTime = int(request.form["start"])
    endTime_temp = request.form["end"]
    if endTime_temp == None:
        endTime = None
    else:
        endTime = int(endTime_temp)

    title = request.form["title"]
    parent_id = request.form.get("parent")

    description = request.form["body"]

    node_id = request.form["node_id"]
    if node_id:
      # node id present, user is updating a node
      # TODO: if allow user update event's parent, might result loop in trees, cause event unable to be displayed
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

    return rerender_edit_page(session["note_id"])

# respond to delete of a node
# TODO: delete a node from note
@bp.route("/edit_delete/<int:id>")
def submit_note_name(id):
    
    sql_query = f"DELETE FROM history_node WHERE id={id}"
    db.session.execute(sql_query)
    db.session.commit()
    return rerender_edit_page(session["note_id"])
