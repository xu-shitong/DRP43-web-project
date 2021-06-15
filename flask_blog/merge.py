from flask import Blueprint, flash, request, jsonify, url_for, render_template, session
from flask_blog.app import db
from flask_blog.db import Note, HistoryNode

bp = Blueprint("merge", __name__)


@bp.route("/merge", methods=["GET", "POST"])
def merge():
    notes = get_all_note_editable_by_user()
    if request.method == 'POST':
        author_id = session["user_id"]
        index1 = int(request.form["first"])
        index2 = int(request.form["second"])
        new_name = request.form["new_name"]
        note1 = Note.query.filter_by(note_name=notes[index1]).first()
        note2 = Note.query.filter_by(note_name=notes[index2]).first()
        id1 = note1.id
        id2 = note2.id
        # print(notes[index1] + " " + notes[index2] + " " + new_name)
        nodes1 = HistoryNode.query.filter_by(note_id=id1).all()
        nodes2 = HistoryNode.query.filter_by(note_id=id2).all()
        note3 = Note(author_id=author_id, note_name=new_name, refs=0, is_public="00")
        db.session.add(note3)
        db.session.commit()
        id3 = Note.query.filter_by(note_name=new_name).first().id
        nodes3 = []
        for node1 in nodes1:
            new_node = HistoryNode(note_id=id3, title=node1.title, start_date=node1.start_date,
                                   end_date=node1.end_date, content=node1.content, parent_node_id=0)
            nodes3.append(new_node)
        for node2 in nodes2:
            new_node = HistoryNode(note_id=id3, title=node2.title, start_date=node2.start_date,
                                   end_date=node2.end_date, content=node2.content, parent_node_id=0)
            nodes3.append(new_node)
        for node3 in nodes3:
            db.session.add(node3)
        db.session.commit()
    return render_template("merge.html", notes=notes)



def get_all_note_editable_by_user():
    user_id = session["user_id"]
    sql_query = f"SELECT note_name FROM note WHERE author_id={user_id}"  # TODO: or
    notes = db.session.execute(sql_query).fetchall()
    notes = [note for (note,) in notes]
    return notes