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


@bp.route("/personal/<int:id>", methods=['GET', 'POST'])
def person(id):
    notes = get_my_note(session)
    name = getName(id)
    return render_template('personal_page.html', name=name, notes=notes, base_note=notes)