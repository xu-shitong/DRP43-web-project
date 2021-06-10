from flask import Blueprint, flash, request, jsonify
from flask.templating import render_template
from flask_blog.app import db


bp = Blueprint("search_page", __name__)

@bp.route("/search", methods=["GET", "POST"])
def search():
  if request.method == "GET":
    return render_template("search_page.html")
  
  # method is post, find the note user searching for
  info = request.form["search_info"]
  
  if (info.startswith('-') and info[1:].isdigit()) or info.isdigit():
    # if search info is a number, treat as time
    time = int(info)
    sql_query = "SELECT * from history_node " \
               f"WHERE start_date <= {time} " \
               f"OR end_date >= {time}"
  else :
    # info is a string, search titles to find a note title contain the info
    sql_query = "SELECT * from history_node " \
                f"WHERE title LIKE '%{info}%'"
  
  notes = db.session.execute(sql_query).fetchall()
  return render_template("search_page.html", notes=notes)