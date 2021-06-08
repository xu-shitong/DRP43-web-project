import re
from flask import (Blueprint, flash, request, session)
from flask.templating import render_template
from werkzeug.utils import redirect
from flask_blog.app import db
import json
bp = Blueprint("edit_page", __name__)

note = {"is_main_page": False,
        "start": 100, "end": 150, 
        "nodes": [[{"node_id": 1, "parent_id": 0,"start": 100, "end": 120, "title": "event 1", "content": "content of event 1"}, 
                  {"node_id": 2, "parent_id": 0,"start": 110, "end": 130, "title": "event 2", "content": "content of event 2"}, 
                  {"node_id": 3, "parent_id": 0,"start": 120, "end": 140, "title": "event 3", "content": "content of event 3"}],
                  [{"node_id": 4, "parent_id": 0,"start": 100, "end": 150, "title": "event 4", "content": "content of event 4"}]]
        }

# on enter edit page, id is note_id
@bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_page(id):
  session.clear()
  session["note_id"] = id
  # TODO: retrieve note from database, 
  #         IS_MAIN_PAGE: boolean field, tell js whether it is main page or edit page
  #         START is the minimum of START variable in nodes, 
  #         END is maximum of END in nodes
  #         NODES is a list of turple, each turple are history nodes of the same priority level, 
  #               the list of turple is sorted in order, from highest priority to lowest priority
  #               priority level is calculated as the number of parent nodes in the spanning tree
  #                  e.g. if node A has no parent, it is the root of spanning tree, priority level 0, in the first list
  #                          node B's parent node is A, then B has priority level 1, in the second list.
  return render_template("edit_page.html", note=json.dumps(note))

# respond to submit of edit page's update
@bp.route("/edit", methods=["POST"])
def submit_note():
  if request.method == "POST":
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
    print(node_id)

    # update datastructure in backend
    for layer in note["nodes"]:
      for entity in layer:
        print(entity["node_id"])
        if entity["node_id"] == int(node_id):
          entity["start"] = startTime
          entity["end"] = endTime
          entity["content"] = description
          entity["parent"] = parent_id
          entity["title"] = title
          print("successful update")
    # TODO: reorganise note datastructure, change which layer the node belong to
    
    # update database
    # sql_query = f'UPDATE historynode' \
    #             f'SET title="{title}", ' \
    #             f'start_date="{startTime}", '\
    #             f'end_date="{endTime}", '\
    #             f'content="{description}", '\
    #             f'parent_node_id="{parent_id}", ' \
    #             f'WHERE note_id = {g.note_id}'

    # db.session.execute(sql_query)
    # db.session.commit()

    return render_template("/edit_page.html", note=json.dumps(note))

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
  return render_template("/edit_page.html", note=json.dumps(note))

  
