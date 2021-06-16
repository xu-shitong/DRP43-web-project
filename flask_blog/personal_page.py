from flask.globals import session
from flask_sqlalchemy.utils import sqlalchemy_version
from werkzeug.utils import redirect
from flask_blog.auth import login_required
from flask_blog.db import Note
from flask import Blueprint, flash, request, jsonify
from flask.templating import render_template
from flask_blog.app import db
from flask_blog.utils import fetchNote, defaultNote, getName, getNoteInfo, get_my_note
import json


bp = Blueprint("person", __name__)


@bp.route("/personal/<int:id>")
def person(id):
    notes = get_my_note(session)
    name = getName(id)
    sql_query = f"SELECT note.id, note_name, note.create_date, username, refs " \
                f"FROM user_favour JOIN note ON note.id = note_id JOIN account ON account.id = note.author_id " \
                f"WHERE user_id = {id}"
    favour_notes = db.session.execute(sql_query).fetchall()
    fields = ["id", "note_name", "create_date", "username", "refs"]
    favour_notes = [dict(zip(fields, favour_note)) for favour_note in favour_notes]
    return render_template('personal_page.html', name=name, notes=notes, base_note=get_my_note(session),
                           favourite_notes=favour_notes)