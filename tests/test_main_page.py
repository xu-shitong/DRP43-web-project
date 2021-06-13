import pytest
from flask_blog.app import initDatabase


def test_main_view(client, auth):
    response = client.get('/main')
    assert b'Log In' in response.data
    assert b'Register' in response.data

    auth.login()
    response = client.get('/main')
    assert b'Log Out' in response.data
    assert b'showing note: None' in response.data
    assert b'id: None' in response.data


# TODO: need to involve account, the scope a user can see (private and public)
def test_main_open_note_by_search(client, auth):
    response = client.post('/main', data={'note_id': 1})
    assert response.status_code == 200
    # TODO: return location is /main/1
    response = client.post('/main', data={'note_id': 2})
    assert response.status_code == 200
    # TODO: return location is /main/1


# TODO: test about accessing /main/5 and /main/5/edit
@pytest.mark.parametrize('path', ('/main/5', '/main/6'))
def test_main_cannot_get_non_existed_blog(client, auth, path):
    auth.login()
    assert client.get(path).status_code == 404



def test_main_cannot_open_others_private_note():
    assert 1 == 1
