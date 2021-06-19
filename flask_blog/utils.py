from pymysql import NULL
from flask_blog.app import db
from flask_blog.db import Account, HistoryNode, Note

# get a partivular note info, DOES NOT verify if user has the priviledge to see/edit it
def getNoteInfo(note_id):
  sql_query = "SELECT * " \
              "FROM note " \
              f"WHERE id = {note_id} "
  return db.session.execute(sql_query).fetchone()

# retrieve note from database, 
#   IS_MAIN_PAGE: boolean field, tell js whether it is main page or edit page
#   START is the minimum of START variable in nodes, 
#   END is maximum of END in nodes
#   NODES is a list of turple, each turple are history nodes of the same priority level, 
#         the list of turple is sorted in order, from highest priority to lowest priority
#         priority level is calculated as the number of parent nodes in the spanning tree
#         e.g. if node A has no parent, it is the root of spanning tree, priority level 0, in the first list
#              node B's parent node is A, then B has priority level 1, in the second list.
def fetchNote(noteId, is_in_main):
  sql_query = "SELECT id, title, start_date, end_date, content, parent_node_id " \
              "FROM history_node " \
              f"WHERE note_id = {noteId} " \
              "ORDER BY start_date"
  entities = db.session.execute(sql_query).fetchall()

  # initialise note as start and end in 0
  print(entities)
  note = defaultNote(is_in_main)
  if entities:
    # if note is not empty, initialise start and end as the first element in it
    note["start"] = entities[0]["start_date"]
    note["end"] = entities[0]["end_date"]

  # record which layer the node are allocated
  idLayerMap = {}

  # record what are the immediate child of the node
  tree = {0: {"title": "(the most general event)", "child": []}}
  
  # record single event
  singles = NULL

  unallocedEntities = entities
  prevLen = 0 # initialise as 0 to avoid conflict with empty unalloc length
  while prevLen != len(unallocedEntities):
    prevLen = len(unallocedEntities)
    entities = unallocedEntities
    unallocedEntities = []

    while entities :
      # while entities is not empty, constantly remove element from it
      entity = entities.pop(0)

      start_date = entity["start_date"]
      end_date = entity["end_date"]

      find_pics = f'SELECT name, path FROM pic_and_name WHERE node_id = {entity["id"]}'
      pics = db.session.execute(find_pics).fetchall()
      fields = ["pic_name", "path"]
      pics = [(dict(zip(fields, pic))) for pic in pics]
      # [{"pic_name": , "path":}, {"pic_name": , "path":}]

      # create node, will be ignored if fail to find parent
      new_one = {
        'node_id': entity["id"], 
        'parent_id': entity["parent_node_id"],
        'start': entity["start_date"], 
        'end': entity["end_date"], 
        'title': entity["title"], 
        'content': entity["content"],
        'pictures': pics
      }

      if start_date == end_date:
        # node is single event, put in singles
        if singles == NULL:
          singles = {"start": start_date, "end": end_date, "nodes": [new_one]}
        else :
          singles["nodes"].append(new_one)
          singles["start"] = min(singles["start"], start_date)
          singles["end"] = max(singles["end"], end_date)

      elif not entity["parent_node_id"]:
        # if node does not have parent, put in layer 1, record in map
        if note["nodes"]:
          note["nodes"][0].append(new_one)
        else:
          note["nodes"] = [[new_one]]

        idLayerMap[new_one["node_id"]] = 0

        # add node in tree, with no child node
        tree[entity["id"]] = {"title": entity["title"], "child": []}
        # add node as child of node 0, the root node
        tree[0]["child"].append(entity["id"])
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

          # add node in tree, with no child node
          tree[entity["id"]] = {"title": entity["title"], "child": []}
          # add node as child of its parent in tree
          tree[entity["parent_node_id"]]["child"].append(entity["id"])
        else:
          # parent has not been added to note, put the elem back to end of entities
          unallocedEntities.append(entity)


      # ensure START and END are outer boundaries of the nodes
      note["start"] = min(note["start"], start_date)
      note["end"] = max(note["end"], end_date)

      if unallocedEntities:
        print(f"remaining entities are not added in note: {unallocedEntities}")

  note["tree"] = tree
  if singles == NULL:
    note["singles"] = {"start": 0, "end": 0, "nodes": []}
  else :
    note["singles"] = singles
  return note


def defaultNote(is_in_main):
  return {"is_in_main": is_in_main, "start": 0, "end": 0, "nodes": [], "singles": {"start": 0, "end": 0, "nodes": []}}

# if logged in, get private note and favourite note
# if not logged in, return empty
def all_notes(session):
  if "user_id" in session:
    # if user logged in
    # fetch notes that belong to the user
    sql_query = private_note_sql(session["user_id"])
    notes = db.session.execute(sql_query).fetchall()

    # fetch notes that are marked as favour, and visible to user
    sql_query = get_note_with_publicity(user_id=session["user_id"], is_favour=True, read='2', write='0')
    notes += db.session.execute(sql_query).fetchall()

    # shared_note = "SELECT note.id, note_name, username, note.is_public FROM note JOIN user_favour "\
    #               "ON note.id=user_favour.note_id " \
    #               "JOIN account ON note.author_id=account.id " \
    #              f"WHERE {session['user_id']}=user_favour.user_id"
    # favour_notes = db.session.execute(shared_note).fetchall()
    
    # # filter notes that are visible to user
    # # TODO: after adding friend ficture, change logic of checking visibility
    # for note in favour_notes:
    #   # if note is visible to public, display, 
    #   if note["is_public"][0] == '2':
    #     notes.append((note["id"], note["note_name"], note["username"]))
  else :
    # # user not logged in, return only public note
    # sql_query = get_note_with_publicity(user_id=None, is_favour=False, read='2', write='0')
    # notes = db.session.execute(sql_query).fetchall()
    notes = []


  fields = ['note id', 'author_id', 'note name', 'create_date', 'refs', 'is_public' ]
  notes_ = ([(dict(zip(fields, note))) for note in notes])
  return notes_
    
# sql of all private note
def private_note_sql(user_id):
  return "SELECT note.id, author_id, note_name, note.create_date, refs, is_public FROM note " \
         f'WHERE {user_id}=note.author_id '

# return private notes, if not logged in, return []
def get_my_note(session):
  if "user_id" in session:
    sql_query = private_note_sql(session["user_id"])
    my_notes = db.session.execute(sql_query).fetchall()
    my_notes = [dict(zip(['id', 'author_id', 'note_name', 'create_date', 'refs', 'is_public' ], my_note)) for my_note in my_notes]
    return my_notes
  return []

# sql of note that visible to user
# if IS_FAVOUR return note that are marked as favourite by user
# READ is minimum read publicity
# WRITE is minimum write publicity
# excluding user private notes
def get_note_with_publicity(user_id, is_favour, read, write):

  # return all field of note
  sql_query = "SELECT DISTINCT note.id, author_id, note_name, create_date, refs, is_public " \
              "FROM note " \
              "WHERE "
  
  
  if user_id:
    # if fetching note for certain user, exclude private note
    sql_query += f"author_id<>{user_id} AND "

    favour_sql = "(SELECT * " \
                  "FROM   user_favour uf " \
                 f"WHERE  uf.user_id = {user_id} " \
                  "AND    uf.note_id = note.id) "
    if is_favour:
      # select all note favoured by user
      sql_query += f"EXISTS {favour_sql} AND "
    else :
      # select all note not favoured by user
      sql_query += f"NOT EXISTS {favour_sql} AND "

  # ELSE: user not logged in, return all note satisfy read write publicity, no additional constrain
  
  # add constrain on read write publicity, -2 -1 means publicity are the last but 2 chars
  sql_query += f"SUBSTRING(note.is_public, -2, 1)>='{read}' " \
               f"AND SUBSTRING(note.is_public, -1, 1)>='{write}' "


  return sql_query

# get user name with given user ID
def getName(id):
    sql_query = f"SELECT username FROM account WHERE id={id}"
    (name,) = db.session.execute(sql_query).fetchone()
    return name

# check if user is invited editor of note
def is_invited_user(user_id, note_id):
    sql_query = f"SELECT * FROM invite_record WHERE invited_user_id={user_id} AND note_id={note_id}"
    hasInviteRecord = db.session.execute(sql_query)
    print(list(hasInviteRecord))
    return hasInviteRecord

# return list of note user invited to edit, may overlap with public notes
def get_invited_note(user_id):
    return "SELECT note.id, author_id, note_name, create_date, refs, is_public FROM note " \
           "JOIN invite_record ON note_id=note.id " \
          f"WHERE invited_user_id={user_id}"

## following variables and functions are for develop/test propose
# note = {"is_main_page": True,
#           "start": 100, "end": 150,
#           "nodes": [[{"start": 100, "end": 120, "title": "event 1", "content": "content of event 1"},
#                     {"start": 110, "end": 130, "title": "event 2", "content": "content of event 2"},
#                     {"start": 120, "end": 140, "title": "event 3", "content": "content of event 3"}],
#                     [{"start": 100, "end": 150, "title": "event 4", "content": "content of event 4"}]]
#           }

# def dbDummyInit():
#   # Dummy initialisation of database
#   db.drop_all()
#   db.create_all()
#   new_one = Account(id=1, username="name", password="123")
#   db.session.add(new_one)
#   db.session.commit()
#   new_one = Note(id=1, note_name="name", author_id=1, references=0)
#   db.session.add(new_one)
#   db.session.commit()
#   note = {"is_main_page": False,
#           "start": 100, "end": 150, 
#           "nodes": [[{"node_id": 1, "parent_id": 0,"start": 100, "end": 120, "title": "event 1", "content": "content of event 1"}, 
#                     {"node_id": 2, "parent_id": 0,"start": 110, "end": 130, "title": "event 2", "content": "content of event 2"}, 
#                     {"node_id": 3, "parent_id": 0,"start": 120, "end": 140, "title": "event 3", "content": "content of event 3"}],
#                     [{"node_id": 4, "parent_id": 1,"start": 100, "end": 150, "title": "event 4", "content": "content of event 4"}]]
#           }
#   for layer in note["nodes"]:
#     for entity in layer:
#       newNode = HistoryNode(
#         note_id=1,
#         title=entity["title"],
#         start_date=entity["start"],
#         end_date=entity["end"],
#         content=entity["content"],
#         parent_node_id=entity["parent_id"]
#       )
#       db.session.add(newNode)
#       db.session.commit()
#   # end dummy initialisation
