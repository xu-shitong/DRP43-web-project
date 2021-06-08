from flask_blog.db import Account, HistoryNode, Note
from html import entities
import re
from flask import (Blueprint, flash, request, session)
from flask.templating import render_template
from werkzeug.utils import redirect
from flask_blog.app import db
import json
bp = Blueprint("edit_page", __name__)

# retrieve note from database, 
#   IS_MAIN_PAGE: boolean field, tell js whether it is main page or edit page
#   START is the minimum of START variable in nodes, 
#   END is maximum of END in nodes
#   NODES is a list of turple, each turple are history nodes of the same priority level, 
#         the list of turple is sorted in order, from highest priority to lowest priority
#         priority level is calculated as the number of parent nodes in the spanning tree
#         e.g. if node A has no parent, it is the root of spanning tree, priority level 0, in the first list
#              node B's parent node is A, then B has priority level 1, in the second list.
def fetchNote(noteId):
  sql_query = "SELECT id, title, start_date, end_date, content, parent_node_id " \
              "FROM history_node " \
              f"WHERE note_id = {noteId} " \
              "ORDER BY start_date"
  entities = db.session.execute(sql_query).fetchall()

  # initialise note as start and end in 0
  note = {"is_in_main": False, 
            "start": 0, "end": 0, 
            "nodes": []}
  if entities:
    # if note is not empty, initialise start and end as the first element in it
    note["start"] = entities[0]["start_date"]
    note["end"] = entities[0]["end_date"]

  # record which layer the node are allocated
  idLayerMap = {}

  unallocedEntities = entities
  prevLen = 0 # initialise as 0 to avoid conflict with empty unalloc length
  while prevLen != len(unallocedEntities):
    prevLen = len(unallocedEntities)
    entities = unallocedEntities
    unallocedEntities = []

    while entities :
      # while entities is not empty, constantly remove element from it
      entity = entities.pop(0)

      # create node, will be ignored if fail to find parent
      new_one = {
        'node_id': entity["id"], 
        'parent_id': entity["parent_node_id"],
        'start': entity["start_date"], 
        'end': entity["end_date"], 
        'title': entity["title"], 
        'content': entity["content"]
      }

      if not entity["parent_node_id"]:
        # if node does not have parent, put in layer 0, record in map
        if note["nodes"]:
          note["nodes"][0].append(new_one)
        else:
          note["nodes"] = [[new_one]]

        idLayerMap[new_one["node_id"]] = 0
      else :
        # find the parent of this node, put it in the layer below its parent
        if entity["parent_node_id"] in idLayerMap:
          parentLayer = idLayerMap[entity["parent_node_id"]]
          # if parent is found, 
          #   1 add node to list lower than parent
          #   2 add the elem entity to idLayerMap so that child of it can look it up

          if len(note["nodes"]) > (parentLayer+1):
            note["nodes"][parentLayer+1].append(new_one)
          else:
            note["nodes"].append([new_one])

          idLayerMap[new_one["node_id"]] = parentLayer+1
        else:
          # parent has not been added to note, put the elem back to end of entities
          unallocedEntities.append(entity)


      # ensure START and END are outer boundaries of the nodes
      note["start"] = min(note["start"], entity["start_date"])
      note["end"] = max(note["end"], entity["end_date"])

      if unallocedEntities:
        print(f"remaining entities are not added in note: {unallocedEntities}")

  print(note)
  return note

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
  return render_template("edit_page.html", note=json.dumps(note))

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
  # return render_template("/edit_page.html", note=json.dumps(note))

  
