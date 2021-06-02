from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from app import Account, Blog, db
from auth import login_required
from werkzeug.exceptions import abort

# from auth import login_required

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    sql_query = "SELECT blog.id, author_id, title, postDate, content " \
                "FROM blog JOIN account ON blog.author_id = account.id"
                # "ORDER BY postDate DESC"
    posts = db.session.execute(sql_query).fetchall()
    return render_template('index.html', posts=posts)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['body']
        error = None
        if not title:
            error = 'Title is required'
        if error is not None:
            flash(error)
        else:
            blog = Blog(author_id=g.user.id, title=title, content=content)
            db.session.add(blog)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template("create.html")


def get_post(id, check_author=True):
    sql_query = "SELECT blog.id, author_id, title, postDate, content " \
                "FROM blog JOIN account ON blog.author_id = account.id " \
                "WHERE blog.id = " + str(id)
    post = db.session.execute(sql_query).fetchone()
    if post is None:
        abort(404, f"Post id {id} doesn't exist")
    # TODO: need to remove this restrict
    if check_author and post['author_id'] != g.user.id:
        abort(403)
    return post


@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['body']
        error = None
        if not title:
            error = 'Title is required'
        if error is not None:
            flash(error)
        else:
            sql_query = f'UPDATE blog SET title="{title}", content="{content}" ' \
                        f'WHERE id = {id}'
            db.session.execute(sql_query)
            db.session.commit()
            return redirect(url_for('blog.index'))
    return render_template('update.html', post=post)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    get_post(id)
    sql_query = f"DELETE FROM blog WHERE id={id}"
    db.session.execute(sql_query)
    db.session.commit()
    return redirect(url_for('blog.index'))

