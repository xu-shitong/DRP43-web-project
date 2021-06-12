from flask.globals import session
from flask.templating import render_template
from flask_blog.app import db
from flask_blog.db import Note
from flask_blog.auth import login_required
from flask import Blueprint, flash, request, jsonify
from flask_blog.auth import login_required
import json

bp = Blueprint("/create_page", __name__)

@bp.route("/create_note", methods=["GET", "POST"])
@login_required
def new_note():
    if request.method == "POST" :
      note_name = request.form["new_note_name"]
      # check user has not created a note of same name
      sql_query = "SELECT id, note_name FROM note "\
                f"WHERE note_name = '{note_name}' " \
                f"AND author_id = {session['user_id']} "
      prevNote = db.session.execute(sql_query).fetchone()
      if prevNote:
        # name conflict with previous note
        print("conflict occure")
        print(prevNote["id"])
        return render_template(f"/create_note.html", href=prevNote["id"], note_name=prevNote["note_name"])


      note = Note(note_name=note_name, author_id=session["user_id"], refs=0)
      print(note_name)
      db.session.add(note)
      db.session.commit()

      # fetch the note_id just added
      sql_query = "SELECT id FROM note "\
                f"WHERE author_id = {session['user_id']} "\
                f"AND note_name = '{note_name}'"
      response = db.session.execute(sql_query).fetchone()
      return render_template(f"/edit/{response['id']}")
    
    return render_template("create_note.html")