from flask import Blueprint, flash, request, jsonify
from flask.templating import render_template
from flask_blog.app import db
from flask_blog.utils import fetchNote, defaultNote
import json
bp = Blueprint("main_page", __name__)


@bp.route("/main", methods=['GET', 'POST'])
def main():
    find_all_notes = "SELECT note.id, note_name, username FROM account JOIN note " \
                     "ON account.id=note.author_id "
    notes = db.session.execute(find_all_notes).fetchall()
    fields = ['note id', 'note name', 'username']
    return_json_notes = ([(dict(zip(fields, note))) for note in notes])
    print(return_json_notes)
    if request.method == 'POST':
        note_id = request.form["note_id"]
        return receive_post(note_id, return_json_notes)
    return render_template("main_page.html", note=json.dumps(defaultNote()), notes=return_json_notes)


def receive_post(note_id, notes):
    note = fetchNote(int(note_id))
    return render_template("main_page.html", note=json.dumps(note), notes=notes)


@bp.route("/main/<int:id>", methods=['GET', 'POST'])
def render_a_note(id):
    note = fetchNote(id)
    find_all_notes = "SELECT note.id, note_name, username FROM account JOIN note " \
                     "ON account.id=note.author_id "
    notes = db.session.execute(find_all_notes).fetchall()
    fields = ['note id', 'note name', 'username']
    notes = ([(dict(zip(fields, note))) for note in notes])
    if request.method == 'POST':
        note_id = request.form["note_id"]
        return receive_post(note_id, notes)
    return render_template('main_page.html', note=json.dumps(note), notes=notes)


