import re
from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from flask_blog.app import db
from flask_blog.db import ForumRecords, Note
from flask_blog.auth import login_required
from flask_blog.utils import get_my_note
import datetime

bp = Blueprint("forum", __name__)


@bp.route("/forum/<int:id>")
@login_required
def board(id):
    session['last_time'] = str(datetime.datetime.now())
    records = find_records(id)
    records =  separate_user_message(records)
    note_name = find_note_name(id)
    return render_template("forum.html", records=records, note_id=id, note_name=note_name,
                           base_note=get_my_note(session))


@bp.route("/forum/<int:id>/refresh", methods=["POST"])
@login_required
def refresh(id):
    records = find_new_records(id, session['last_time'])
    records =  separate_user_message(records)

    session['last_time'] = str(datetime.datetime.now())
    # print(session['user_id'], session['last_time'])
    return jsonify(records_=records)


@bp.route("/forum/<int:id>/add", methods=['POST'])
@login_required
def add(id):
    user_id = session["user_id"]
    content = request.form["content"]
    time = str(datetime.datetime.now())
    forum_record = ForumRecords(user_id=user_id, note_id=id, content=content,
                                create_date=time)
    session["last_time"] = time
    db.session.add(forum_record)
    db.session.commit()
    return redirect(url_for("forum.board", id=id))
                            # records=find_records(id), note_id=id,
                            #  note_name=find_note_name(id)))


def find_records(note_id):
    sql_query = "SELECT username, forum_records.create_date, content, account.id " \
                "FROM forum_records JOIN account ON account.id = user_id " \
                f"WHERE note_id = {note_id} " \
                f"ORDER BY forum_records.create_date ASC"
    records = db.session.execute(sql_query).fetchall()
    records = formal_time(records)
    fields = ["username", "time", "content", "user_id"]
    records = [dict(zip(fields, record)) for record in records]
    return records


def find_new_records(note_id, time):
    sql_query = "SELECT username, forum_records.create_date, content, account.id " \
                "FROM forum_records JOIN account ON account.id = user_id " \
                f"WHERE note_id = {note_id} AND forum_records.create_date > '{time}' " \
                f"ORDER BY forum_records.create_date ASC"
    records = db.session.execute(sql_query).fetchall()
    fields = ["username", "time", "content", "user_id"]
    records = [dict(zip(fields, record)) for record in records]
    return records


def find_note_name(id):
    return Note.query.filter_by(id=id).first().note_name

# mark each message record as send by current user or other users
def separate_user_message(records):
    # add a boolean mark if current user ownes the message
    def add_mark(record):
      record["of_curr_user"] = record["user_id"] == session["user_id"]
      return record
    return [ add_mark(record) for record in records]

def formal_time(record):
    if len(record) == 0:
        return record
    return [(a, str(b)[0:19], c, d) for (a, b, c, d) in record]
    # a, b, c = record
    # return a, b, c[0:19]
