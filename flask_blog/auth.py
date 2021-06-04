import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify)
from werkzeug.security import check_password_hash, generate_password_hash

from flask_blog.app import Account, db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # username = request.args.get('username', 0, type=str)
        # password = request.args.get('password', 0, type=str)
        username = request.form['username']
        password = request.form['password']
        error = None
        if not username:
            error = 'username is required'
        elif not password:
            error = 'password is required'
        elif not validateKey(username):
            error = 'already registered'
        if error is None:
            new_one = Account(username=username, password=password)
            db.session.add(new_one)
            db.session.commit()
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    # if len(request.args) > 0:
    #     username = request.args.get('username', 0, type=str)
    #     password = request.args.get('password', 0, type=str)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        record_user = Account.query.filter_by(username=username).first()
        if record_user is None:
            error = 'Incorrect username.'
        elif not record_user.password == password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = record_user.id
            return redirect(url_for('index'))
        flash(error)

    return render_template('login.html')


def validateKey(username):
    record = Account.query.filter_by(username=username).first()
    return record is None


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        # g.user = db.session.execute(
        #     'SELECT * FROM user WHERE id = ?', (user_id,)
        # ).fetchone()
        g.user = Account.query.filter_by(id=user_id).first()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

