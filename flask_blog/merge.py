from flask import Blueprint, flash, request, jsonify, url_for, render_template, session
from flask_blog.app import db
from flask_blog.db import Note, HistoryNode
from flask_blog.utils import get_my_note, get_note_with_publicity
from flask_blog.auth import login_required

bp = Blueprint("merge", __name__)


@bp.route("/merge", methods=["GET", "POST"])
@login_required
def merge():
    notes = get_my_note(session)
    my_favour_sql = get_note_with_publicity(session["user_id"], is_favour=True, read='2', write='2')
    notes += db.session.execute(my_favour_sql).fetchall()
    if request.method == 'POST':
        author_id = session["user_id"]
        index1 = int(request.form["first"])
        index2 = int(request.form["second"])
        new_name = request.form["new_name"]
        note1 = Note.query.filter_by(note_name=notes[index1]["note_name"]).first()
        note2 = Note.query.filter_by(note_name=notes[index2]["note_name"]).first()
        id1 = note1.id
        id2 = note2.id
        # print(notes[index1] + " " + notes[index2] + " " + new_name)
        nodes1 = HistoryNode.query.filter_by(note_id=id1).all()
        nodes2 = HistoryNode.query.filter_by(note_id=id2).all()
        note3 = Note(author_id=author_id, note_name=new_name, refs=0, is_public="00")
        db.session.add(note3)
        db.session.commit()
        id3 = Note.query.filter_by(note_name=new_name).first().id
        change_in_id = {0: 0}
        id = get_last_id()

        for node1 in nodes1:
            id = id + 1
            new_node = HistoryNode(id=id, note_id=id3, title=node1.title, start_date=node1.start_date,
                                   end_date=node1.end_date, content=node1.content, parent_node_id=0)
            db.session.add(new_node)
            change_in_id[node1.id] = id
        db.session.commit()
        for node1 in nodes1:
            new_id = change_in_id[node1.id]
            new_parent_id = change_in_id[node1.parent_node_id]
            sql_query = f'UPDATE history_node SET parent_node_id={new_parent_id} ' \
                        f'WHERE id="{new_id}"'
            db.session.execute(sql_query)
            db.session.commit()

        change_in_id = {0: 0}
        for node2 in nodes2:
            id = id + 1
            new_node = HistoryNode(note_id=id3, title=node2.title, start_date=node2.start_date,
                                   end_date=node2.end_date, content=node2.content, parent_node_id=0)
            db.session.add(new_node)
            change_in_id[node2.id] = id
        db.session.commit()
        for node2 in nodes2:
            new_id = change_in_id[node2.id]
            new_parent_id = change_in_id[node2.parent_node_id]
            sql_query = f'UPDATE history_node SET parent_node_id={new_parent_id} ' \
                        f'WHERE id="{new_id}"'
            db.session.execute(sql_query)
            db.session.commit()

    return render_template("merge.html", notes=notes, base_note=get_my_note(session))


# ABANDONED, can be substituted by function in util
# def get_all_note_editable_by_user():
#     user_id = session["user_id"]
#     sql_query = f"SELECT note_name FROM note WHERE author_id={user_id}"  # TODO: or
#     notes = db.session.execute(sql_query).fetchall()
#     notes = [note for (note,) in notes]
#     return notes


def find_hierarchy(nodes):
    hierarchy = {}
    for node in nodes:
        node_id = node.id
        parent_id = node.parent_node_id
        if parent_id in hierarchy:
            hierarchy[parent_id].append(node_id)
        else:
            hierarchy[parent_id] = [node_id]
    return hierarchy


def get_last_id():
    sql_query = "SELECT id FROM history_node ORDER BY id DESC"
    (id,) = db.session.execute(sql_query).fetchone()
    return id

