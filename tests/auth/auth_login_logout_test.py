import pytest
import requests

from src.config import url
from tests.helpers import clear

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


# Login
def test_auth_login_v2_incorrect_email(clear_and_register):
    # with pytest.raises(InputError):
    #     auth_login_v1('randomemail@email.com', TEST_PASSWORD)

    resp = requests.post(
        url + '/auth/login/v2',
        json={
            "email": 'randomemail@email.com',
            "password": TEST_PASSWORD
        }
    )

    assert resp.status_code == 400


def test_auth_login_v2_incorrect_password(clear_and_register):
    # with pytest.raises(InputError):
    #     auth_login_v1(TEST_EMAIL, 'randompassword123')

    resp = requests.post(
        url + '/auth/login/v2',
        json={
            "email": TEST_EMAIL,
            "password": "randompassword123"
        }
    )

    assert resp.status_code == 400


def test_auth_login_v2_successful_login(clear_and_register):
    login_user_resp = requests.post(
        url + '/auth/login/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )

    assert login_user_resp.status_code == 200
    assert login_user_resp.json()['auth_user_id'] == 2
    
    # Test token
    channels_create_resp = requests.post(
        url + '/channels/create/v2',
        json={
            "token": login_user_resp.json()['token'],
            "name": "TestChannelName",
            "is_public": True
        }
    )

    assert channels_create_resp.status_code == 200


# def test_auth_login_v1_input_type(clear_and_register):
#     with pytest.raises(InputError):
#         # Test each parameter that requires strings with integers
#         auth_login_v1(12345, 12345)


def test_auth_login_v2_output_type(clear_and_register):
    # Test and see if the response variables have the appropriate types
    login_user_resp = requests.post(
        url + '/auth/login/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )

    assert login_user_resp.status_code == 200

    # auth_user_id is int
    # token is str
    assert isinstance(login_user_resp.json()['auth_user_id'], int)
    assert isinstance(login_user_resp.json()['token'], str)


# Logout
def test_logout_v1_invalid_token(clear_and_register):
    resp = requests.post(
        url + '/auth/logout/v1',
        json={
            "token": "ThisIsAnInvalidToken"
        }
    )

    assert resp.status_code == 403


def test_logout_v1_expired_token(clear_and_register):
    requests.post(
        url + '/auth/logout/v1',
        json={
            "token": pytest.user1_json['token']
        }
    )
    
    channels_create_resp = requests.post(
        url + '/channels/create/v2',
        json={
            "token": pytest.user1_json['token'],
            "name": "TestChannelName",
            "is_public": True
        }
    )

    assert channels_create_resp.status_code == 403


def test_successful_logout_v1(clear_and_register):
    resp = requests.post(
        url + '/auth/logout/v1',
        json={
            "token": pytest.user1_json['token']
        }
    )

    assert resp.status_code == 200
