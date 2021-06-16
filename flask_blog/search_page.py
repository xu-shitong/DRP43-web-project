from re import U
from flask_blog.utils import get_note_with_publicity, private_note_sql
from os import write
from flask_blog.db import UserFavour, Note
from flask.globals import session
from flask_blog.auth import login_required
from flask import Blueprint, flash, request, jsonify, session
from flask.templating import render_template
from flask_blog.app import db
from flask_blog.utils import get_my_note

bp = Blueprint("search_page", __name__)


@bp.route("/search", methods=["GET", "POST"])
def search():
    hot_notes = get_popular_note()
    print(hot_notes)
    fields = ['id', 'author_id', 'note_name', 'create_date', 'refs', 'is_public']
    hot_notes = ([(dict(zip(fields, note))) for note in hot_notes])
    if request.method == "GET":
        return render_template("search_page.html", hot_notes=hot_notes)

    # method is post, find the note user searching for
    info = request.form["search_info"]

    # # TODO: record start and end time in note database
    # if (info.startswith('-') and info[1:].isdigit()) or info.isdigit():
    #   # if search info is a number, treat as time

    # info is a string, search titles to find a note title contain the info
    print(info)
    if info:
      
        # if user logged in, include private notes in search result
        if "user_id" in session:
            user_id = session["user_id"]
            sql_query = private_note_sql(session["user_id"]) + f' AND note_name LIKE "%{info}%"'
            private_notes = db.session.execute(sql_query).fetchall()

            sql_query = get_note_with_publicity(user_id=user_id, is_favour=True, read='2', write='0') + f" AND note_name LIKE '%{info}%'"
            favour_notes = db.session.execute(sql_query).fetchall()

            sql_query = get_note_with_publicity(user_id=user_id, is_favour=False, read='2', write='0') + f" AND note_name LIKE '%{info}%'"
            non_favour_notes = db.session.execute(sql_query).fetchall()
        else :
            user_id = None
            private_notes = []
            favour_notes = []

            sql_query = get_note_with_publicity(user_id=None, is_favour=False, read='2', write='0') + f" AND note_name LIKE '%{info}%'"
            non_favour_notes = db.session.execute(sql_query).fetchall()
    else:
        favour_notes = []
        non_favour_notes = []
        private_notes = []

    # notes are ones displaied in menu dropdown box, favour_notes, non_favour_notes, private notes are notes containing the keyword
    return render_template("search_page.html", private_notes=private_notes, favour_notes=favour_notes, non_favour_notes=non_favour_notes, hot_notes=hot_notes, 
                           base_note=get_my_note(session))


def get_popular_note():
    # user is looking at notes not added to favourate before, no need to include notes visible to user
    sql_query = get_note_with_publicity(user_id=None, is_favour=False, read='2', write='0') + "ORDER BY refs DESC"
    notes = db.session.execute(sql_query).fetchall()
    return notes[:10]


@bp.route("/search/<int:note_id>", methods=["POST"])
def add_favourite(note_id):
    # if not logged in, redirect to login page
    # CANNOT be solved by @login_required, since html used ajax post
    if not "user_id" in session:
        return "failed to add favourite, you need to login first"

    # add entity in favourite database
    record = UserFavour.query.filter_by(user_id=session["user_id"], note_id=note_id).first()
    new_favour = UserFavour(user_id=session["user_id"], note_id=note_id)
    if record is None:
        db.session.add(new_favour)
        old_note = Note.query.filter_by(id=note_id).first()
        refs = max(old_note.refs + 1, 0)
        sql_query = f"UPDATE note SET refs={refs} WHERE id = {note_id}"
        db.session.execute(sql_query)
        db.session.commit()
        # flash("success on delete favour", "success")
        return jsonify(message_="success on add favour " + str(note_id), like=1)
    else:
        db.session.delete(record)
        old_note = Note.query.filter_by(id=note_id).first()
        refs = max(old_note.refs - 1, 0)
        sql_query = f"UPDATE note SET refs={refs} WHERE id = {note_id}"
        db.session.execute(sql_query)
        db.session.commit()
        # flash("success on delete favour", "success")
        return jsonify(message_="success on delete favour" + str(note_id), like=0)

