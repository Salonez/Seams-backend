import requests
import pytest

from tests.helpers import clear
from src.helpers import create_jwt_session_token
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


def test_create_jwt_session_token_invalid_id(clear_and_register):
    requests.post(
        url + '/auth/register/v2',
        json={
            "email": "abc@defe.com",
            "password": TEST_PASSWORD,
            "name_first": "another",
            "name_last": "name"
        }
    )
    assert create_jwt_session_token(0) is None
    assert create_jwt_session_token(100) is None

    assert create_jwt_session_token(2) is not None