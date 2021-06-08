from flask import Blueprint
from flask.templating import render_template
import json
bp = Blueprint("edit_page", __name__)


@bp.route("/edit")
def edit():
    note = {"is_main_page": False,
            "start": 100, "end": 150,
            "nodes": [[{"start": 100, "end": 120, "title": "event 1", "content": "content of event 1"},
                       {"start": 110, "end": 130, "title": "event 2", "content": "content of event 2"},
                       {"start": 120, "end": 140, "title": "event 3", "content": "content of event 3"}],
                      [{"start": 100, "end": 150, "title": "event 4", "content": "content of event 4"}]]
            }
    return render_template("edit_page.html", note=json.dumps(note))
