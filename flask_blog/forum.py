from flask import Blueprint, render_template, session, request, redirect, url_for
from flask_blog.app import db
from flask_blog.db import ForumRecords, Note
from flask_blog.auth import login_required

bp = Blueprint("forum", __name__)


@bp.route("/forum/<int:id>")
@login_required
def board(id):
    records = find_records(id)
    note_name = find_note_name(id)
    return render_template("forum.html", records=records, note_id=id, note_name=note_name)


@bp.route("/forum/<int:id>/add", methods=['POST'])
@login_required
def add(id):
    user_id = session["user_id"]
    content = request.form["content"]
    forum_record = ForumRecords(user_id=user_id, note_id=id, content=content)
    db.session.add(forum_record)
    db.session.commit()
    return redirect(url_for("forum.board", id=id))
                            # records=find_records(id), note_id=id,
                            #  note_name=find_note_name(id)))


def find_records(note_id):
    sql_query = "SELECT username, forum_records.create_date, content " \
                "FROM forum_records JOIN account ON account.id = user_id " \
                f"WHERE note_id = {note_id} " \
                f"ORDER BY forum_records.create_date ASC"
    records = db.session.execute(sql_query).fetchall()
    fields = ["username", "time", "content"]
    records = [dict(zip(fields, record)) for record in records]
    return records


def find_note_name(id):
    return Note.query.filter_by(id=id).first().note_name
