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
    refs = db.Column(db.INT, nullable=False)
    is_public = db.Column(db.VARCHAR(5), nullable=False, default="00")


class HistoryNode(db.Model):
    id = db.Column(db.INT, primary_key=True, nullable=False)
    note_id = db.Column(db.INT, db.ForeignKey('note.id'), nullable=False)
    title = db.Column(db.VARCHAR(50), nullable=False)
    start_date = db.Column(db.INT, nullable=False)
    end_date = db.Column(db.INT, nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_node_id = db.Column(db.INT, nullable=False)


class PicAndName(db.Model):
    id = db.Column(db.INT, primary_key=True, nullable=False)
    node_id = db.Column(db.INT, db.ForeignKey('history_node.id'), nullable=False)
    name = db.Column(db.VARCHAR(100))
    path = db.Column(db.VARCHAR(100), nullable=False)


class UserFavour(db.Model):
    user_id = db.Column(db.INT, db.ForeignKey('account.id'), primary_key=True, nullable=False)
    note_id = db.Column(db.INT, db.ForeignKey('note.id'), primary_key=True, nullable=False)


class InviteRecord(db.Model):
    invited_user_id = db.Column(db.INT, db.ForeignKey('account.id'), primary_key=True, nullable=False)
    note_id = db.Column(db.INT, db.ForeignKey('account.id'), primary_key=True, nullable=False)


class ForumRecords(db.Model):
    id = db.Column(db.INT, primary_key=True, nullable=False)
    note_id = db.Column(db.INT, db.ForeignKey('note.id'), nullable=False)
    user_id = db.Column(db.INT, db.ForeignKey('account.id'), nullable=False)
    content = db.Column(db.TEXT, nullable=False)
    create_date = db.Column(db.VARCHAR(50), nullable=False)


def completeClassInit():
    return db
