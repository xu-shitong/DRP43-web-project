import pytest
import sys
sys.path.extend(['../'])
from flask_blog.app import getApp, getDatabase


@pytest.fixture
# each test will firstly call getDatabase(True), which drop_all then create_all
def app():
    app = getApp()
    with app.app_context():
        print("in app_context")
        # initialise database
        init_db_test(getDatabase(True))
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="test1", password="test1"):
        return self._client.post('/auth/login',
                                 data={'username': username, 'password': password}
                                 )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)


def init_db_test(db):
    db.session.execute("INSERT INTO account (username, password) VALUES ('test1', 'test1')")
    db.session.execute("INSERT INTO blog (author_id, title, postDate, content) "
                       "VALUES "
                       "(1, 'test title', '2021-6-3 10:00:00', 'this is blog test');")
    db.session.commit()


def restore_db_test(db):
    db.session.execute("DELETE FROM account WHERE username='test1'")
    db.session.execute("DELETE FROM blog WHERE title='test title'")
    db.session.commit()
