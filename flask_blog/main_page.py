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
from flask_blog.utils import fetchNote, defaultNote, getNoteInfo, get_my_note, get_note_with_publicity
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

        # fetch note name, if user gave a bad note id, redirect to 404
        note_info = getNoteInfo(note_id)
        if note_info:
            note_name = note_info["note_name"]

            # check if user has permission to write to note
            if "user_id" in session :
                edit_permission = (session["user_id"] == note_info["author_id"]) or (note_info["is_public"][0] == '2')
            else :
                # user not logged in, permission is false
                edit_permission = False 
        else:
            return render_template("error/404.html", message=f"note with id: {note_id} not found")
    else:
        # no note_id given, return empty note content and name 
        note = defaultNote(is_in_main=True)
        note_name = None
        edit_permission = False

    return render_template('main_page.html', note=json.dumps(note), note_id=note_id, note_name=note_name,
                           base_note=get_my_note(session), edit_permission=edit_permission)


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


