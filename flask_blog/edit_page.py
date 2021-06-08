import itertools
from flask_blog.db import Account, HistoryNode, Note
from html import entities
import re
from flask import (Blueprint, flash, request, session)
from flask.templating import render_template
from werkzeug.utils import redirect
from flask_blog.app import db
from flask_blog.utils import fetchNote
import json
bp = Blueprint("edit_page", __name__)

# on enter edit page, id is note_id
@bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_page(id):
  session.clear()
  session["note_id"] = id

  # # Dummy initialisation of database
  # db.drop_all()
  # db.create_all()
  # new_one = Account(id=1, username="name", password="123")
  # db.session.add(new_one)
  # db.session.commit()
  # new_one = Note(id=1, note_name="name", author_id=1, references=0)
  # db.session.add(new_one)
  # db.session.commit()
  # note = {"is_main_page": False,
  #         "start": 100, "end": 150, 
  #         "nodes": [[{"node_id": 1, "parent_id": 0,"start": 100, "end": 120, "title": "event 1", "content": "content of event 1"}, 
  #                   {"node_id": 2, "parent_id": 0,"start": 110, "end": 130, "title": "event 2", "content": "content of event 2"}, 
  #                   {"node_id": 3, "parent_id": 0,"start": 120, "end": 140, "title": "event 3", "content": "content of event 3"}],
  #                   [{"node_id": 4, "parent_id": 1,"start": 100, "end": 150, "title": "event 4", "content": "content of event 4"}]]
  #         }
  # for layer in note["nodes"]:
  #   for entity in layer:
  #     newNode = HistoryNode(
  #       note_id=session["note_id"],
  #       title=entity["title"],
  #       start_date=entity["start"],
  #       end_date=entity["end"],
  #       content=entity["content"],
  #       parent_node_id=entity["parent_id"]
  #     )
  #     db.session.add(newNode)
  #     db.session.commit()
  # # end dummy initialisation


  note = fetchNote(noteId=id)
  summary = itertools.chain.from_iterable(note["nodes"])
  return render_template("edit_page.html", note=json.dumps(note), summary=summary)

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

  # TODO: if allow user update event's parent, might result loop in trees, cause event unable to be displayed
  # update database
  sql_query = f'UPDATE history_node ' \
              f'SET title="{title}", ' \
              f'start_date="{startTime}", '\
              f'end_date="{endTime}", '\
              f'content="{description}", '\
              f'parent_node_id="{parent_id}" ' \
              f'WHERE id = {node_id}'

  db.session.execute(sql_query)
  db.session.commit()
  note = fetchNote(session["note_id"])
  summary = itertools.chain.from_iterable(note["nodes"])

  return render_template("/edit_page.html", note=json.dumps(note), summary=summary)

# respond to submit of new note name
@bp.route("/submit_note_name", methods=["POST"])
def submit_note_name():
  note_name = request.form["note_name"]
  if note_name == None:
    flash("note name cannot be empty")
  else :  
    sql_query = f'UPDATE note SET notename="{note_name}" ' \
                f'WHERE note_id = {session["note_id"]}'
    db.session.execute(sql_query)
    db.session.commit()
  # return render_template("/edit_page.html", note=json.dumps(note))

  
