import requests
import pytest

from tests.helpers import clear
from src.config import url
from src.error import AccessError, InputError

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


def test_decorators_token_required_did_not_provide_json_payload(clear_and_register):
    resp = requests.post(
        url + "channels/create/v2"
    )

    assert resp.status_code == AccessError.code

    resp = requests.post(
        url + "channels/create/v2",
        json={}
    )

    assert resp.status_code == AccessError.code



def test_decorators_token_required_did_not_provide_token_in_json_payload(clear_and_register):
    resp = requests.post(
        url + "channels/create/v2",
        json={
            "name": "hello",
            "is_public": True
        }
    )

    assert resp.status_code == AccessError.code


    
