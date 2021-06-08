from flask import (Blueprint, flash, request)
from flask.templating import render_template
from flask_blog.app import db
import json
bp = Blueprint("main_page", __name__)

note = {}
note_id = 0

@bp.route("/edit/<int:note_id>")
def edit():
  # TODO: note should be retrieved from database, 
  #         IS_MAIN_PAGE: boolean field, tell js whether it is main page or edit page
  #         START is the minimum of START variable in nodes, 
  #         END is maximum of END in nodes
  #         NODES is a list of turple, each turple are history nodes of the same priority level, 
  #               the list of turple is sorted in order, from highest priority to lowest priority
  #               priority level is calculated as the number of parent nodes in the spanning tree
  #                  e.g. if node A has no parent, it is the root of spanning tree, priority level 0, in the first list
  #                          node B's parent node is A, then B has priority level 1, in the second list.
  note = {"is_main_page": True,
          "start": 100, "end": 150, 
          "nodes": [[{"start": 100, "end": 120, "title": "event 1", "content": "content of event 1"}, 
                    {"start": 110, "end": 130, "title": "event 2", "content": "content of event 2"}, 
                    {"start": 120, "end": 140, "title": "event 3", "content": "content of event 3"}],
                    [{"start": 100, "end": 150, "title": "event 4", "content": "content of event 4"}]]
          }
  return render_template("main_page.html", note=json.dumps(note))

# respond to submit of edit page's update
@bp.route("/sumbit", methods=["POST"])
def submit_note():
  # TODO: update database data, update NOTE, rerender edit page
  return render_template("/edit_page.html", note=json.dumps(note))

# respond to submit of new note name
@bp.route("/submit_note_name", methods=["POST"])
def submit_note_name():
  note_name = request.form["note_name"]
  if note_name == None:
    flash("note name cannot be empty")
  else :  
    sql_query = f'UPDATE note SET notename="{note_name}" ' \
                f'WHERE note_id = {note_id}'
    db.session.execute(sql_query)
    db.session.commit()
  return render_template("/edit_page.html", note=json.dumps(note))

  