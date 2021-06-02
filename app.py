from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://zhangziheng:@106.52.101.201:3306/accounts'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "123"
db = SQLAlchemy(app)
pymysql.install_as_MySQLdb()


class Account(db.Model):
    id = db.Column(db.INT, primary_key=True, nullable=False)
    username = db.Column(db.VARCHAR(20),  nullable=False)
    password = db.Column(db.VARCHAR(100), nullable=False)


class Blog(db.Model):
    id = db.Column(db.INT, primary_key=True, nullable=False)
    author_id = db.Column(db.INT, db.ForeignKey('account.id'), nullable=False)
    # author_id = db.Column(db.INT, nullable=False)
    title = db.Column(db.VARCHAR(100), nullable=False)
    postDate = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow())
    content = db.Column(db.TEXT, nullable=False)


db.create_all()


# @app.route('/')
# def hello_world():
#     return render_template("base.html")


import auth
app.register_blueprint(auth.bp)
import blog
app.register_blueprint(blog.bp)
app.add_url_rule('/', endpoint='index')

if __name__ == '__main__':
    app.run()
