from flask.globals import session
from flask.helpers import url_for
from flask_sqlalchemy.utils import sqlalchemy_version
from werkzeug.utils import redirect
from flask_blog.auth import login_required
from flask_blog.db import Note
from flask import Blueprint, flash, request, jsonify
from flask.templating import render_template
from flask_blog.app import db
from flask_blog.utils import fetchNote, defaultNote, getNoteInfo
import json
bp = Blueprint("main_page", __name__)

def all_notes():
    # fetch all notes, available for user to choose to view
    find_all_notes = "SELECT note.id, note_name, username FROM account JOIN note " \
                     "ON account.id=note.author_id "
    notes = db.session.execute(find_all_notes).fetchall()
    fields = ['note id', 'note name', 'username']
    notes = ([(dict(zip(fields, note))) for note in notes])
    return notes

# if no note is passed in, meaning no note is displaying. otherwise, display the given note
#    note_id is the displaying note's id
def display_notes(note_id=None):
    if request.method == "POST":
        # if user is fetching new note, set note_id
        note_id = request.form["note_id"]

    if note_id:
        # fetch note content, if fetch fail, fetchNote will return default note
        note = fetchNote(note_id, is_in_main=True)

        # fetch note name, if user gave a bad note id, redirect to 404
        note_info = getNoteInfo(note_id)
        if note_info:
            note_name = note_info["note_name"]
        else:
            return render_template("error/404.html", message=f"note with id: {note_id} not found")
    else:
        # no note_id given, return empty note content and name 
        note = defaultNote(is_in_main=True)
        note_name = None

    # fetch all notes, available for user to choose to view
    notes = all_notes()

    return render_template('main_page.html', note=json.dumps(note), notes=notes, note_id=note_id, note_name=note_name)

# first enter of main page, no note displaying 
@bp.route("/main", methods=['GET', 'POST'])
def main():
    return display_notes()
    
# on displaying a note in main page, with note_id = ID
@bp.route("/main/<int:id>", methods=['GET', 'POST'])
def render_a_note(id):
    return display_notes(id)

@bp.route("/new_note/<note_name>", methods=["POST"])
@login_required
def new_note(note_name):
    # TODO: check user has not created a note of same name
    sql_query = "SELECT id, note_name FROM note "\
               f"WHERE note_name = '{note_name}' " \
               f"AND author_id = {session['user_id']} "
    prevNote = db.session.execute(sql_query).fetchone()
    if prevNote:
      # name conflict with previous note
      print("conflict occure")
      print(prevNote["id"])
      # TODO: change response to turple of note info
      return json.dumps({"href": prevNote["id"], "note_name": prevNote["note_name"]})


    note = Note(note_name=note_name, author_id=session["user_id"], refs=0)
    print(note_name)
    db.session.add(note)
    db.session.commit()

    # fetch the note_id just added
    sql_query = "SELECT id FROM note "\
               f"WHERE author_id = {session['user_id']} "\
               f"AND note_name = '{note_name}'"
    response = db.session.execute(sql_query).fetchone()
    return json.dumps(response["id"])