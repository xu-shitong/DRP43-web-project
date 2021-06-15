from flask.globals import session
from flask.templating import render_template
from werkzeug.utils import redirect
from flask_blog.app import db
from flask_blog.db import Note
from flask_blog.auth import login_required
from flask import Blueprint, flash, request, jsonify
from flask_blog.auth import login_required
from flask_blog.utils import get_my_note
import json

bp = Blueprint("/create_page", __name__)

@bp.route("/create_note", methods=["GET", "POST"])
@login_required
def new_note():
    if request.method == "POST" :
      note_name = request.form["new_note_name"]
      # # check user has not created a note of same name
      # sql_query = "SELECT id, note_name FROM note "\
      #           f"WHERE note_name = '{note_name}' " \
      #           f"AND author_id = {session['user_id']} "
      # prevNote = db.session.execute(sql_query).fetchone()
      # if prevNote:
      #   # name conflict with previous note
      #   print("conflict occure")
      #   print(prevNote["id"])
      #   return render_template(f"/create_note.html", href=prevNote["id"], note_name=prevNote["note_name"])

      read = request.form["read"]
      write = request.form["write"]
      isPublic = read + write
      
      note = Note(note_name=note_name, author_id=session["user_id"], refs=0, is_public=isPublic)
      print(note_name)
      db.session.add(note)
      db.session.commit()

      # fetch the note_id just added
      sql_query = "SELECT LAST_INSERT_ID()"
      note = db.session.execute(sql_query).fetchone()
      node_id = note["LAST_INSERT_ID()"]
      return redirect(f"/edit/{node_id}")
    
    return render_template("create_note.html", base_note=get_my_note(session))