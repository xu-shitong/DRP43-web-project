from flask.globals import session
from flask_sqlalchemy.utils import sqlalchemy_version
from werkzeug.utils import redirect
from flask_blog.auth import login_required
from flask_blog.db import Note
from flask import Blueprint, flash, request, jsonify
from flask.templating import render_template
from flask_blog.app import db
from flask_blog.utils import fetchNote, defaultNote, getName, getNoteInfo, get_invited_note, get_my_note, get_note_with_publicity
import json


bp = Blueprint("person", __name__)


@bp.route("/personal/<int:id>")
def person(id):
    notes = get_my_note(session)
    name = getName(id)
    sql_query = get_note_with_publicity(user_id=id, is_favour=True, read='1', write='0')
    favour_notes = db.session.execute(sql_query).fetchall()
    fields = ["id", "author_id", "note_name", "create_date", "refs", "is_public"]
    favour_notes = [dict(zip(fields, favour_note)) for favour_note in favour_notes]
    
    sql_query = get_invited_note(user_id=id)
    invited_note = db.session.execute(sql_query).fetchall()
    invited_note = ([(dict(zip(fields, note))) for note in invited_note])

    return render_template('personal_page.html', name=name, user_id=id, notes=notes, base_note=get_my_note(session),
                           favourite_notes=favour_notes, invited_note=invited_note)