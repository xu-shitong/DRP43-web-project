import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify)
from werkzeug.security import check_password_hash, generate_password_hash

from app import Account, db

bp = Blueprint('new_auth_name', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if len(request.args) > 0:
        username = request.args.get('username', 0, type=str)
        password = request.args.get('password', 0, type=str)
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
            return jsonify(result="Success")
            
        flash(error)
    return render_template('account.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if len(request.args) > 0:
        username = request.args.get('username', 0, type=str)
        password = request.args.get('password', 0, type=str)
        error = None
        record_user = Account.query.filter_by(username=username).first()
        if record_user is None:
            error = 'Incorrect username.'
        elif not record_user.password == password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = record_user.username
            return jsonify(result="Login Succeed")
        else:
            return jsonify(result=error)
        # flash(error)

    return render_template('login.html')


def validateKey(username):
    record = Account.query.filter_by(username=username).first()
    print(username)
    print(Account.query.filter_by(username=username))
    print(record)
    print(record is None)
    return record is None
