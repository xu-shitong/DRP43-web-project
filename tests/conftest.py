import pytest
import sys
# sys.path.extend(['../'])  
from flask_blog.app import getApp, initDatabase


@pytest.fixture
# each test will firstly call getDatabase(True), which drop_all then create_all
def app():
    app = getApp()
    with app.app_context():
        print("in app_context")
        # initialise database
        init_db_test(initDatabase(True))
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# class AuthActions(object):
#     def __init__(self, client):
#         self._client = client
#
#     def login(self, username="test1", password="test1"):
#         return self._client.post('/auth/login',
#                                  data={'username': username, 'password': password}
#                                  )
#
#     def logout(self):
#         return self._client.get('/auth/logout')


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="Amy", password="Amy"):
        return self._client.post('/auth/login',
                                 data={'username': username, 'password': password}
                                 )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)


# def init_db_test(db):
#     db.session.execute("INSERT INTO account (create_date, username, password) "
#                        "VALUES ('2021-6-3 10:00:00', 'test1', 'test1')")
#     db.session.execute("INSERT INTO blog (author_id, title, postDate, content) "
#                        "VALUES "
#                        "(1, 'test title', '2021-6-3 10:00:00', 'this is blog test');")
#     db.session.commit()


def restore_db_test(db):
    db.session.execute("DELETE FROM account WHERE username='test1'")
    db.session.execute("DELETE FROM blog WHERE title='test title'")
    db.session.commit()


def init_db_test(db):
    sql_query1 = "INSERT INTO account (create_date, username, password) " \
                 "VALUES ('2021-6-3 10:00:00', 'Amy', 'Amy')"
    sql_query2 = "INSERT INTO note (author_id, note_name, create_date, refs, is_public) " \
                 "VALUES (1, 'The Tang Dynasty', '2021-6-3 10:00:00', 0, 1)"
    sql_query3 = "INSERT INTO history_node (note_id, title, start_date, end_date, content, parent_node_id) " \
                 "VALUES ('1', 'Flourishment Age of Kaiyuan Era', '712', '741', 'content', 0)"
    sql_query4 = "INSERT INTO history_node (note_id, title, start_date, end_date, content, parent_node_id) " \
                 "VALUES ('1', 'Government of Zhenguan', '627', '649', 'society developed quickly', 0)"
    sql_query5 = "INSERT INTO note (author_id, note_name, create_date, refs, is_public) " \
                 "VALUES (1, 'The Qin Dynasty', '2021-6-3 10:00:00', 0, 0)"
    sql_query6 = "INSERT INTO history_node (note_id, title, start_date, end_date, content, parent_node_id) " \
                 "VALUES ('2', 'Building Great Wall', '-214', '-170', 'large labour force to build Great World')"
    sql_query7 = "INSERT INTO history_node (note_id, title, start_date, end_date, content, parent_node_id) " \
                 "VALUES ('1', 'The Tang Dynasty establishment and destory', '618', '907', 'content', 0)"
    sql_query8 = "INSERT INTO account (create_date, username, password) " \
                 "VALUES ('2021-6-3 10:00:00', 'Bob', 'Bob')"
    sql_query9 = "INSERT INTO note (author_id, note_name, create_date, refs, is_public)" \
                 "VALUES ('2', 'test node name', '2021-6-3 10:00:00', 2)"
    sql_query10 = "INSERT INTO history_node (note_id, title, start_date, end_date, content, parent_node_id) " \
                  "VALUES ('2', 'test node (time period)', '1000', '2000', 'test content', 0)"
    db.session.execute(sql_query1)
    db.session.execute(sql_query2)
    db.session.execute(sql_query3)
    db.session.execute(sql_query4)
    db.session.execute(sql_query5)
    db.session.execute(sql_query6)
    db.session.execute(sql_query7)
    db.session.execute(sql_query8)
    db.session.execute(sql_query9)
    db.session.commit()