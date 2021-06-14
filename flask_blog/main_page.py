from os import write
import re
from flask.globals import session
from flask_sqlalchemy.utils import sqlalchemy_version
from werkzeug.utils import redirect
from flask_blog.auth import login_required
from flask_blog.db import Note
from flask import Blueprint, flash, request, jsonify, url_for, make_response
from flask.templating import render_template
from flask_blog.app import db
from flask_blog.utils import fetchNote, defaultNote, getNoteInfo, get_note_with_publicity, get_private_note
import json
bp = Blueprint("main_page", __name__)


def all_notes():
    print(session)
    if "user_id" in session:
        # if user logged in
        # fetch notes that belong to the user
        notes = get_private_note(session["user_id"])

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
        # user not logged in, return only public note
        sql_query = get_note_with_publicity(user_id=None, is_favour=False, read='2', write='0')
        notes = db.session.execute(sql_query).fetchall()


    fields = ['note id', 'author_id', 'note name', 'create_date', 'refs', 'is_public' ]
    notes_ = ([(dict(zip(fields, note))) for note in notes])
    return notes_

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


@bp.route("/main/pics/<path>", methods=['GET', 'POST'])
def render_a_pic(path):
    image_data = open("../pics/"+path, "rb").read()
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/jpg'
    return response


