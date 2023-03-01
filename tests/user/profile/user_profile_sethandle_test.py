import requests
import pytest

from tests.helpers import clear
from src.config import url

TEST_EMAIL = 'steve@steve.com'
TEST_PASSWORD = 'bestpasswordever123'
TEST_NAME_FIRST = 'Steve'
TEST_NAME_LAST = 'Jobs'
TEST_HANDLE_STR = 'stevejobs'


@pytest.fixture
def clear_and_register():
    clear()
    return requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    ).json()


def test_user_profile_sethandle_v1_length(clear_and_register):
    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": clear_and_register['token'],
            "handle_str": ''
        }
    )

    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": clear_and_register['token'],
            "handle_str": 'a'*1
        }
    )

    assert resp.status_code == 400

    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": clear_and_register['token'],
            "handle_str": 'a'*2
        }
    )

    assert resp.status_code == 400

    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": clear_and_register['token'],
            "handle_str": 'a'*21
        }
    )

    assert resp.status_code == 400

    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": clear_and_register['token'],
            "handle_str": 'a'*100
        }
    )
    assert resp.status_code == 400


def test_user_profile_sethandle_v1_contains_non_alphanumeric(clear_and_register):
    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": clear_and_register['token'],
            "handle_str": 'ThisIsATest!@#'
        }
    )
    assert resp.status_code == 400

    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": clear_and_register['token'],
            "handle_str": '!!!'
        }
    )
    assert resp.status_code == 400

    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": clear_and_register['token'],
            "handle_str": '()()'
        }
    )
    assert resp.status_code == 400


def test_user_profile_sethandle_v1_already_used(clear_and_register):
    resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": 'atestemail@google.com',
            "password": TEST_PASSWORD,
            "name_first": 'Bill',
            "name_last": 'Gates'
        }
    )

    token = resp.json()['token']

    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": token,
            "handle_str": 'stevejobs'
        }
    )
    assert resp.status_code == 400

    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": clear_and_register['token'],
            "handle_str": 'billgates'
        }
    )
    assert resp.status_code == 400


def test_user_profile_sethandle_v1_successful(clear_and_register):
    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": clear_and_register['token'],
            "handle_str": 'billgates'
        }
    )
    assert resp.status_code == 200

    # Check whether change is in effect
    user_profile_resp = requests.get(
        url + 'user/profile/v1',
        params={
            'token': clear_and_register['token'],
            'u_id': clear_and_register['auth_user_id']
        }
    )

    assert user_profile_resp.json()['user']['handle_str'] == 'billgates'
