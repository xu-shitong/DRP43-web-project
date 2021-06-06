from flask import (Blueprint, flash)
from flask.templating import render_template

bp = Blueprint("main_page", __name__)

@bp.route("/main")
def main():
  note = [{"time": 1900, 
           "title": "some event", 
           "description": "some description"}]
  return render_template("main_page.html", note=note)
