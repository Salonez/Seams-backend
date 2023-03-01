import requests
import pytest

from tests.helpers import clear
from src.config import url

TEST_EMAIL = 'steve@steve.com'
TEST_PASSWORD = 'bestpasswordever123'
TEST_NAME_FIRST = 'Steve'
TEST_NAME_LAST = 'Jobs'


@pytest.fixture
def clear_and_register():
    clear()
    pytest.pretestuser_json = requests.post(
        url + '/auth/register/v2',
        json={
            "email": "abc@def.com",
            "password": TEST_PASSWORD,
            "name_first": "another",
            "name_last": "name"
        }
    ).json()
    pytest.user1_json = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    ).json()
    pytest.posttestuser_json = requests.post(
        url + '/auth/register/v2',
        json={
            "email": "abcdef@def.com",
            "password": TEST_PASSWORD,
            "name_first": "another",
            "name_last": "name"
        }
    ).json()


def test_user_profile_setname_v1_name_first_length(clear_and_register):
    resp = requests.put(
        url + 'user/profile/setname/v1',
        json={
            "token": pytest.user1_json['token'],
            "name_first": '',
            "name_last": TEST_NAME_LAST
        }
    )
    assert resp.status_code == 400

    resp = requests.put(
        url + 'user/profile/setname/v1',
        json={
            "token": pytest.user1_json['token'],
            "name_first": 'a'*100,
            "name_last": TEST_NAME_LAST
        }
    )
    assert resp.status_code == 400


def test_user_profile_setname_v1_name_last_length(clear_and_register):
    resp = requests.put(
        url + 'user/profile/setname/v1',
        json={
            "token": pytest.user1_json['token'],
            "name_first": TEST_NAME_FIRST,
            "name_last": ''
        }
    )
    assert resp.status_code == 400

    resp = requests.put(
        url + 'user/profile/setname/v1',
        json={
            "token": pytest.user1_json['token'],
            "name_first": TEST_NAME_FIRST,
            "name_last": 'a'*100
        }
    )
    assert resp.status_code == 400


def test_user_profile_setname_v1_successful(clear_and_register):
    resp = requests.put(
        url + 'user/profile/setname/v1',
        json={
            "token": pytest.user1_json['token'],
            "name_first": 'Bill',
            "name_last": 'Gates'
        }
    )
    assert resp.status_code == 200

    # Check whether change is in effect
    user_profile_resp = requests.get(
        url + 'user/profile/v1',
        params={
            'token': pytest.user1_json['token'],
            'u_id': pytest.user1_json['auth_user_id']
        }
    )

    assert user_profile_resp.json()['user']['name_first'] == 'Bill'
    assert user_profile_resp.json()['user']['name_last'] == 'Gates'

    
