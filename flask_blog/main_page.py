from flask import Blueprint, flash, request
from flask.templating import render_template
from flask_blog.app import db
from flask_blog.utils import fetchNote
import json
bp = Blueprint("main_page", __name__)


@bp.route("/main", methods=['GET', 'POST'])
def main():
    """ TODO: note should be retrieved from database,
          IS_MAIN_PAGE: boolean field, tell js whether it is main page or edit page
          START is the minimum of START variable in nodes,
          END is maximum of END in nodes
          NODES is a list of turple, each turple are history nodes of the same priority level,
                the list of turple is sorted in order, from highest priority to lowest priority
                priority level is calculated as the number of parent nodes in the spanning tree
                   e.g. if node A has no parent, it is the root of spanning tree, priority level 0, in the first list
                           node B's parent node is A, then B has priority level 1, in the second list.
    """
    note = {"is_main_page": True,
          "start": 100, "end": 150, 
          "nodes": [[{"start": 100, "end": 120, "title": "event 1", "content": "content of event 1"}, 
                    {"start": 110, "end": 130, "title": "event 2", "content": "content of event 2"}, 
                    {"start": 120, "end": 140, "title": "event 3", "content": "content of event 3"}],
                    [{"start": 100, "end": 150, "title": "event 4", "content": "content of event 4"}]]
          }

    if request.method == 'POST':

        note_id = request.form['note_id']
        # find_all_nodes_sql = \
        #     f"SELECT title, start_date, end_date, content FROM history_node " \
        #     f"WHERE note_id={note_id} ORDER BY parent_node_id DESC"
        # history_nodes = db.session.execute(find_all_nodes_sql).fetchall()
        # fields = ["title", "start_date", "end_date", "content"]
        # dicts = [str(dict(zip(fields, history_node))) for history_node in history_nodes]

        # find_start_sql = f"SELECT min(start_date) FROM history_node WHERE note_id={note_id}"
        # find_end_sql = f"SELECT max(start_date) FROM history_node WHERE note_id={note_id}"
        # (start,) = db.session.execute(find_start_sql).first()
        # (end,) = db.session.execute(find_end_sql).first()
        # return_fields = ["is_main", "start", "end", "nodes"]
        # return_json = json.dumps(dict(zip(return_fields, [True, start, end, dicts])))
        # return return_json
        note = fetchNote(note_id)
        return render_template("main_page.html", note=json.dumps(note))
    return render_template("main_page.html", note=json.dumps(note))


# @bp.route('/create', methods=['GET', 'POST'])
# @login_required
# def create():
#     if request.method == 'POST':
#         title = request.form['title']
#         content = request.form['body']
#         error = None
#         if not title:
#             error = 'Title is required'
#         if error is not None:
#             flash(error)
#         else:
#             blog = Blog(author_id=g.user.id, title=title, content=content)
#             db.session.add(blog)
#             db.session.commit()
#             return redirect(url_for('index'))
#     return render_template("create.html")

