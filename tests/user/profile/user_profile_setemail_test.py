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
    return requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    ).json()


def test_user_profile_setemail_v1_invalid_email(clear_and_register):
    resp = requests.put(
        url + 'user/profile/setemail/v1',
        json={
            "token": clear_and_register['token'],
            "email": "steve!steve"
        }
    )
    assert resp.status_code == 400


def test_user_profile_setemail_v1_email_already_in_use(clear_and_register):
    requests.post(
        url + '/auth/register/v2',
        json={
            "email": "bill@bill.com",
            "password": TEST_PASSWORD,
            "name_first": "Bill",
            "name_last": "Gates"
        }
    ).json()

    resp = requests.put(
        url + 'user/profile/setemail/v1',
        json={
            "token": clear_and_register['token'],
            "email": "bill@bill.com"
        }
    )
    assert resp.status_code == 400


def test_user_profile_setemail_v1_successful(clear_and_register):
    resp = requests.put(
        url + 'user/profile/setemail/v1',
        json={
            "token": clear_and_register['token'],
            "email": 'alegitemail@google.com'
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

    assert user_profile_resp.json()['user']['email'] == 'alegitemail@google.com'
