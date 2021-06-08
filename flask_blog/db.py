from datetime import datetime

from flask_blog.app import db


class Account(db.Model):
    id = db.Column(db.INT, primary_key=True, nullable=False)
    create_date = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow())
    username = db.Column(db.VARCHAR(20),  nullable=False)
    password = db.Column(db.VARCHAR(100), nullable=False)


class Blog(db.Model):
    id = db.Column(db.INT, primary_key=True, nullable=False)
    author_id = db.Column(db.INT, db.ForeignKey('account.id'), nullable=False)
    title = db.Column(db.VARCHAR(100), nullable=False)
    postDate = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow())
    content = db.Column(db.TEXT, nullable=False)


class Note(db.Model):
    id = db.Column(db.INT, primary_key=True, nullable=False)
    author_id = db.Column(db.INT, db.ForeignKey('account.id'), nullable=False)
    note_name = db.Column(db.VARCHAR(50), nullable=False)
    create_date = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow())
    references = db.Column(db.INT, nullable=False)


class HistoryNode(db.Model):
    id = db.Column(db.INT, primary_key=True, nullable=False)
    note_id = db.Column(db.INT, db.ForeignKey('note.id'), nullable=False)
    title = db.Column(db.VARCHAR(50), nullable=False)
    start_date = db.Column(db.INT, nullable=False)
    end_date = db.Column(db.INT, nullable=True)
    content = db.Column(db.Text, nullable=False)
    parent_node_id = db.Column(db.INT, nullable=True)


def completeClassInit():
    return db