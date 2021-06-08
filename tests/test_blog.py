import pytest
from flask_blog.app import initDatabase


def test_index_view(client, auth):
    response = client.get('/')
    assert b'Log In' in response.data
    assert b'Register' in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'this is blog test' in response.data
    assert b'href="/1/update' in response.data
    # assert b'by on' in response.data


def test_2(client, auth):
    auth.login()
    print("\n")
    # TODO: what is the difference between client.get and client.post
    print(client.get('/create').status_code)      # 200
    print(client.post('/create').status_code)     # 400
    print(client.get("/1/update").status_code)    # 200
    print(client.post("/1/update").status_code)   # 400
    # print(client.get("/1/delete").status_code)  # 405 delete only allow post
    print(client.post("/1/delete").status_code)   # 302 after delete, redirect


@pytest.mark.parametrize('path', ('/create', '/1/update', '/1/delete'))
def test_paths_that_required_login(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_only_authors_can_modify_post(app, client, auth):
    # first add a second user 'test2' and a new blog by 'test2'
    # then check if first user 'test1' can modify blog of 'test2'
    with app.app_context():
        db = initDatabase()
        db.session.execute("INSERT INTO account (create_date, username, password) "
                           "VALUES ('2021-6-3 10:00:00', 'test2', 'test2')")
        db.session.execute("INSERT INTO blog (author_id, title, postDate, content) "
                           "VALUES (2, 'test title 2', '2021-6-3 10:00:00', 'this is blog test2')")
        db.session.commit()

    auth.login()
    assert client.get('/2/update').status_code == 403        # cannot modify
    assert client.post('/2/delete').status_code == 403       # cannot delete
    assert b'href="/1/update"' in client.get('/').data       # can see edit link of test1's blog
    assert b'href="/2/update"' not in client.get('/').data   # cannot see edit link


@pytest.mark.parametrize('path', ('/2/delete', '/2/update'))
def test_cannot_get_non_existed_blog(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        db = initDatabase()
        post = db.session.execute('SELECT * FROM blog WHERE id=1').fetchone()
        assert post is None