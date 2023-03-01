import pytest
import requests

from src import config

from src.error import *

@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')
    pytest.user1 = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    pytest.user2 = requests.post(config.url + 'auth/register/v2', json={'email': 'testadmin@test.com', 'password': 'password', 'name_first': 'Nicholas', 'name_last': 'Decsease'})
    pytest.channel1 = requests.post(config.url + 'channels/create/v2', json={'token': pytest.user1.json()['token'], 'name': 'testchannel', 'is_public': True})
    pytest.channel2 = requests.post(config.url + 'channels/create/v2', json={'token': pytest.user2.json()['token'], 'name': 'testchannel', 'is_public': False})
    pytest.dm1 = requests.post(config.url + "/dm/create/v1", json={'token': pytest.user1.json()['token'], 'u_ids': [2]})
    pytest.dm2 = requests.post(config.url + "/dm/create/v1", json={'token': pytest.user2.json()['token'], 'u_ids': []})
    return

def test_normal_function(clear_and_register):
    message = requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id']})
    resp = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'start': 0})
    assert resp.json()['messages'] == []

def test_incorrect_message_id(clear_and_register):
    requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user1.json()['token'], 'message_id': 0 })
    assert resp.status_code == InputError.code

def test_wasnt_sent_by_user(clear_and_register):
    requests.post(config.url + 'channel/join/v2', json={'token': pytest.user2.json()['token'], 'channel_id': pytest.channel1.json()['channel_id']})
    message = requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id'] })
    assert resp.status_code == AccessError.code

def test_user_not_in_channel(clear_and_register):
    message = requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id'] })
    assert resp.status_code == InputError.code

def test_wasnt_sent_by_user_but_is_owner(clear_and_register):
    requests.post(config.url + 'channel/join/v2', json={'token': pytest.user2.json()['token'], 'channel_id': pytest.channel1.json()['channel_id']})
    message = requests.post(config.url + 'message/send/v1', json={'token': pytest.user2.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'] })
    assert resp.json() == {}

def test_dm_normal_function(clear_and_register):
    message = requests.post(config.url + 'message/senddm/v1', json={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'message': "Hi"})
    message2 = requests.post(config.url + 'message/senddm/v1', json={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'message': "Hi"})
    requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id']})
    requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user1.json()['token'], 'message_id': message2.json()['message_id']})
    resp = requests.get(config.url + 'dm/messages/v1', params={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'start': 0})
    assert resp.json()['messages'] == []

def test_dm_incorrect_message_id(clear_and_register):
    requests.post(config.url + 'message/senddm/v1', json={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'message': "Hi"})
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user1.json()['token'], 'message_id': 0 })
    assert resp.status_code == InputError.code

def test_dm_wasnt_sent_by_user(clear_and_register):
    message = requests.post(config.url + 'message/senddm/v1', json={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'message': "Hi"})
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id'] })
    assert resp.status_code == AccessError.code

def test_dm_wasnt_sent_by_user_but_is_owner(clear_and_register):
    message = requests.post(config.url + 'message/senddm/v1', json={'token': pytest.user2.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'message': "Hi"})
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'] })
    assert resp.json() == {}