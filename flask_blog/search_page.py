from flask import Blueprint, flash, request, jsonify
from flask.templating import render_template
from flask_blog.app import db

bp = Blueprint("search_page", __name__)


@bp.route("/search", methods=["GET", "POST"])
def search():
    hot_notes = get_popular_note()
    fields = ['id', 'note_name', 'refs']
    hot_notes = ([(dict(zip(fields, note))) for note in hot_notes])
    if request.method == "GET":
        return render_template("search_page.html", hot_notes=hot_notes)

    # method is post, find the note user searching for
    info = request.form["search_info"]

    # # TODO: record start and end time in note database
    # if (info.startswith('-') and info[1:].isdigit()) or info.isdigit():
    #   # if search info is a number, treat as time

    # info is a string, search titles to find a note title contain the info
    if info:
        sql_query = "SELECT * from note " \
                    f"WHERE note_name LIKE '%{info}%'"
        notes = db.session.execute(sql_query).fetchall()
    else:
        notes = []

    return render_template("search_page.html", notes=notes, hot_notes=hot_notes)


def get_popular_note():
    sql_query = "SELECT id, note_name, refs FROM note ORDER BY refs DESC"
    notes = db.session.execute(sql_query).fetchall()
    return notes[:10]
