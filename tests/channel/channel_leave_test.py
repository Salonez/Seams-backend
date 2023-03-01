import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.error import *
from tests.helpers import clear

@pytest.fixture
def clear_and_register():
    clear()
    user_for_coverage = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cover', 'name_last': 'Age'})
    requests.post(config.url + 'channels/create/v2', json={'token': user_for_coverage.json()['token'], 'name': 'Coverage channel', 'is_public': True})

def test_valid_member_leave(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'testchannel', 'is_public': True})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'testadmin@test.com', 'password': 'password', 'name_first': 'Nicholas', 'name_last': 'Decsease'})
    requests.post(config.url + 'channel/join/v2', json={'token': member.json()['token'], 'channel_id': channel.json()['channel_id']})
    member_message = requests.post(config.url + 'message/send/v1', json={'token': member.json()['token'], 'channel_id': channel.json()['channel_id'], 'message': 'Nicholas was here'})
    status = requests.post(config.url + 'channel/leave/v1', json={'token': member.json()['token'], 'channel_id': channel.json()['channel_id']})
    assert status.status_code == 200
    resp = requests.get(config.url + 'channel/details/v2', params={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id']})
    for members in resp.json()['all_members']:
        assert member.json()['auth_user_id'] != members['u_id']
    message = requests.get(config.url + 'channel/messages/v2', params={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id'], 'start': 0})
    assert message.json()['messages'][0]['message_id'] == member_message.json()['message_id']

def test_owner_leave(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': owner.json()['token'], 'name': 'testchannel', 'is_public': True})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'testadmin@test.com', 'password': 'password', 'name_first': 'Nicholas', 'name_last': 'Decsease'})
    requests.post(config.url + 'channel/join/v2', json={'token': member.json()['token'], 'channel_id': channel.json()['channel_id']})
    owner_message = requests.post(config.url + 'message/send/v1', json={'token': owner.json()['token'], 'channel_id': channel.json()['channel_id'], 'message': 'Nicholas was here'})
    status = requests.post(config.url + 'channel/leave/v1', json={'token': owner.json()['token'], 'channel_id': channel.json()['channel_id']})
    assert status.status_code == 200
    resp = requests.get(config.url + 'channel/details/v2', params={'token': member.json()['token'], 'channel_id': channel.json()['channel_id']})
    for members in resp.json()['all_members']:
        assert owner.json()['auth_user_id'] != members['u_id']
    for owners in resp.json()['owner_members']:
        assert owner.json()['auth_user_id'] != owners['u_id']
    message = requests.get(config.url + 'channel/messages/v2', params={'token': member.json()['token'], 'channel_id': channel.json()['channel_id'], 'start': 0})
    assert message.json()['messages'][0]['message_id'] == owner_message.json()['message_id']

def test_only_member_leaves(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': owner.json()['token'], 'name': 'testchannel', 'is_public': True})
    status = requests.post(config.url + 'channel/leave/v1', json={'token': owner.json()['token'], 'channel_id': channel.json()['channel_id']})
    assert status.status_code == 200
    # Could check more he by using listall to check the channel still exists.

def test_invalid_channel_id(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    invalid_channel = 9999
    status = requests.post(config.url + 'channel/leave/v1', json={'token': creator.json()['token'], 'channel_id': invalid_channel})
    assert status.status_code == 400

def test_non_member_leave(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'testchannel', 'is_public': True})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'testadmin@test.com', 'password': 'password', 'name_first': 'Nicholas', 'name_last': 'Decsease'})
    status = requests.post(config.url + 'channel/leave/v1', json={'token': member.json()['token'], 'channel_id': channel.json()['channel_id']})
    assert status.status_code == 403