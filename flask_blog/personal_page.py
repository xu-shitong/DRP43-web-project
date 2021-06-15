from flask.globals import session
from flask_sqlalchemy.utils import sqlalchemy_version
from werkzeug.utils import redirect
from flask_blog.auth import login_required
from flask_blog.db import Note
from flask import Blueprint, flash, request, jsonify
from flask.templating import render_template
from flask_blog.app import db
from flask_blog.utils import fetchNote, defaultNote, getNoteInfo, get_my_note
import json


bp = Blueprint("person", __name__)


@bp.route("/personal/<name>", methods=['GET', 'POST'])
def person(name):
    notes = getMyNote(name)
    fields = ['id', 'note_name', 'create_date', 'refs']
    notes = ([(dict(zip(fields, note))) for note in notes])
    return render_template('personal_page.html', name=name, notes=notes, base_note=get_my_note(session["user_id"]))


def getMyNote(name):
    sql_query = "SELECT note.id, note_name, note.create_date, refs " \
                "FROM note JOIN account ON author_id = account.id " \
                f"WHERE username = '{name}'"
    notes = db.session.execute(sql_query).fetchall()
    return notes