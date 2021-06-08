import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql

DATABASE_ACCOUNT = os.environ["DATABASE_ACCOUNT"]
DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
DATABASE_DOMAIN_NAME = os.environ["DATABASE_DOMAIN_NAME"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
APP_CONFIG_KEY = os.environ["APP_CONFIG_KEY"]

app = Flask(__name__)


def setDatabase(app, test=False):
    app.config['SQLALCHEMY_DATABASE_URI'] \
        = 'mysql://' + DATABASE_ACCOUNT + ':' + DATABASE_PASSWORD + '@' \
          + DATABASE_DOMAIN_NAME + ':3306/' + DATABASE_NAME
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://localhost:3306/accounts'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = APP_CONFIG_KEY
    # app.config['SECRET_KEY'] = "123"
    db = SQLAlchemy(app)
    pymysql.install_as_MySQLdb()
    return db


db = setDatabase(app)


def initDatabase(new=False):
    from flask_blog.db import completeClassInit
    db = completeClassInit()
    if new:
        db.drop_all()
    db.create_all()
    return db


db = initDatabase()


@app.route('/hello')
def hello_world():
    return "Hello World"


import flask_blog.auth as auth
app.register_blueprint(auth.bp)
import flask_blog.blog as blog
app.register_blueprint(blog.bp)
import flask_blog.main_page as main
app.register_blueprint(main.bp)
import flask_blog.edit_page as edit
app.register_blueprint(edit.bp)
app.add_url_rule('/', endpoint='index')


def getApp():
    return app


if __name__ == '__main__':
    app.run()
