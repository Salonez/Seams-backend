import pytest
import requests
from src import config
from src.error import *
from tests.helpers import clear

@pytest.fixture
def clear_and_register():
    clear()
    pytest.creator = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'}).json()
    pytest.member = requests.post(config.url + 'auth/register/v2', json={'email': 'testadmin@test.com', 'password': 'password', 'name_first': 'Nicholas', 'name_last': 'Decsease'}).json()
    pytest.dm = requests.post(config.url + 'dm/create/v1', json={'token': pytest.creator['token'], 'u_ids': [pytest.member['auth_user_id']]}).json()


def test_valid_member_leave(clear_and_register):
    member_message = requests.post(config.url + 'message/senddm/v1', json={'token': pytest.member['token'], 'dm_id': pytest.dm['dm_id'], 'message': 'Nicholas was here'})
    status = requests.post(config.url + 'dm/leave/v1', json={'token': pytest.member['token'], 'dm_id': pytest.dm['dm_id']})
    assert status.status_code == 200

    resp = requests.get(config.url + 'dm/details/v1', params={'token': pytest.creator['token'], 'dm_id': pytest.dm['dm_id']})

    for dm_member in resp.json()['members']:
        assert pytest.member['auth_user_id'] != dm_member['u_id']

    message = requests.get(config.url + 'dm/messages/v1', params={'token': pytest.creator['token'], 'dm_id': pytest.dm['dm_id'], 'start': 0})
    assert message.json()['messages'][0]['message_id'] == member_message.json()['message_id']


def test_owner_leave(clear_and_register):
    owner_message = requests.post(config.url + 'message/senddm/v1', json={'token': pytest.creator['token'], 'dm_id': pytest.dm['dm_id'], 'message': 'Nicholas was here'})
    status = requests.post(config.url + 'dm/leave/v1', json={'token': pytest.creator['token'], 'dm_id': pytest.dm['dm_id']})
    assert status.status_code == 200

    resp = requests.get(config.url + 'dm/details/v1', params={'token': pytest.member['token'], 'dm_id': pytest.dm['dm_id']})

    for members in resp.json()['members']:
        assert pytest.creator['auth_user_id'] != members['u_id']

    message = requests.get(config.url + 'dm/messages/v1', params={'token': pytest.member['token'], 'dm_id': pytest.dm['dm_id'], 'start': 0})
    assert message.json()['messages'][0]['message_id'] == owner_message.json()['message_id']


def test_all_members_leaves(clear_and_register):
    status = requests.post(config.url + 'dm/leave/v1', json={'token': pytest.creator['token'], 'dm_id': pytest.dm['dm_id']})
    assert status.status_code == 200
    resp = requests.get(config.url + 'dm/details/v1', json={'token': pytest.creator['token'], 'dm_id': pytest.dm['dm_id']})
    assert resp.status_code == 403

    status = requests.post(config.url + 'dm/leave/v1', json={'token': pytest.member['token'], 'dm_id': pytest.dm['dm_id']})
    assert status.status_code == 200
    resp = requests.get(config.url + 'dm/details/v1', json={'token': pytest.member['token'], 'dm_id': pytest.dm['dm_id']})
    assert resp.status_code == 403


def test_invalid_dm_id(clear_and_register):
    invalid_dm = 9999
    status = requests.post(config.url + 'dm/leave/v1', json={'token': pytest.creator['token'], 'dm_id': invalid_dm})
    assert status.status_code == 400


def test_non_member_leave(clear_and_register):
    status = requests.post(config.url + 'dm/leave/v1', json={'token': pytest.member['token'], 'dm_id': pytest.dm['dm_id']})
    status = requests.post(config.url + 'dm/leave/v1', json={'token': pytest.member['token'], 'dm_id': pytest.dm['dm_id']})
    assert status.status_code == 403

    test_user = requests.post(config.url + 'auth/register/v2', json={'email': 'fakeemail@email.com', 'password': 'password', 'name_first': 'Nicholas', 'name_last': 'Decsease'}).json()
    status = requests.post(config.url + 'dm/leave/v1', json={'token': test_user['token'], 'dm_id': pytest.dm['dm_id']})
    assert status.status_code == 403
