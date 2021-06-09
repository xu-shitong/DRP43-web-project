from flask import Blueprint, flash, request, jsonify
from flask.templating import render_template
from flask_blog.app import db
from flask_blog.utils import fetchNote, defaultNote, getNoteInfo
import json
bp = Blueprint("main_page", __name__)

# if no note is passed in, meaning no note is displaying. otherwise, display the given note
#    note_id is the displaying note's id
def display_notes(note_id=None):
    if request.method == "POST":
        # if user is fetching new note, set note_id
        note_id = request.form["note_id"]

    if note_id:
        # fetch note content, if fetch fail, fetchNote will return default note
        note = fetchNote(note_id, is_in_main=True)

        # fetch note name, if user gave a bad note id, note name set to None
        note_info = getNoteInfo(note_id)
        note_name = None
        if note_info:
            note_name = note_info["note_name"]
    else :
        # no note_id given, return empty note content and name 
        note = defaultNote(is_in_main=True)
        note_name = None

    # fetch all notes, available for user to choose to view
    find_all_notes = "SELECT note.id, note_name, username FROM account JOIN note " \
                     "ON account.id=note.author_id "
    notes = db.session.execute(find_all_notes).fetchall()
    fields = ['note id', 'note name', 'username']
    notes = ([(dict(zip(fields, note))) for note in notes])

    return render_template('main_page.html', note=json.dumps(note), notes=notes, note_id=note_id, note_name=note_name)

# first enter of main page, no note displaying 
@bp.route("/main", methods=['GET', 'POST'])
def main():
    return display_notes()
    
# on displaying a note in main page, with note_id = ID
@bp.route("/main/<int:id>", methods=['GET', 'POST'])
def render_a_note(id):
    return display_notes(id)


