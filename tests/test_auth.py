import pytest
from flask import g, session
from flask_blog.app import initDatabase


def test_register_view(client):
    assert client.get('auth/register').status_code == 200

# TODO: check return address is correct
# def test_register(client, app):
#     response = client.post(
#         '/auth/register', data={'username': 'a', 'password': 'a'}
#     )
#     assert 'http://localhost/auth/login' == response.headers['Location']


def test_register_post_database_update(client, app):
    response = client.post('/auth/register', data={'username': 'aa', 'password': 'aa'})
    with app.app_context():
        assert initDatabase().session.execute("SELECT * FROM account WHERE username='aa'") \
                   .fetchone() is not None
    # getDatabase().session.execute("DELETE FROM account WHERE username='aa'")
    # getDatabase().session.commit()


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '', b'username is required'),
        ('a', '', b'password is required'),
        ('test1', 'test1', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post('/auth/register', data={'username': username, 'password': password})
    assert message in response.data


def test_login_view(client, auth):
    assert client.get('/auth/login').status_code == 200


# def test_login_session_update(client, app, auth):
#     response = auth.login()
#     with client:
#         client.get('/')
#         # TODO: check userid when new database can be set for testing
#         # assert session['user_id'] == 1
#         with app.app_context():
#           assert g.user.username == 'test1'


@pytest.mark.parametrize(('username', 'password', 'message'), (
                         ('abc', 'abc', b'Incorrect username'),
                         ('test1', '2', b'Incorrect password'),))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


# def test_logout(client, auth):
#     auth.login()
#     with client:
#         auth.logout()
#         assert 'user_id' not in session

