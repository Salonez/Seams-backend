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
    pytest.dm1 = requests.post(config.url + 'dm/create/v1', json={'token': pytest.user1.json()['token'], 'u_ids': [2]})
    pytest.dm2 = requests.post(config.url + 'dm/create/v1', json={'token': pytest.user1.json()['token'], 'u_ids': []})
    return

def test_standard_messages(clear_and_register):
    message = requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Test"})
    requests.post(config.url + 'message/pin/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id']})
    resp = requests.post(config.url + 'message/unpin/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id']})
    assert resp.status_code == 200

def test_user_not_in_channel(clear_and_register):
    message = requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Test"})
    requests.post(config.url + 'message/pin/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id']})
    resp = requests.post(config.url + 'message/unpin/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id']})
    assert resp.status_code == InputError.code

def test_user_not_in_dm(clear_and_register):
    message = requests.post(config.url + 'message/senddm/v1', json={'token':pytest.user1.json()['token'],'dm_id':pytest.dm2.json()['dm_id'],'message':"Test"})
    requests.post(config.url + 'message/pin/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id']})
    resp = requests.post(config.url + 'message/unpin/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id']})
    assert resp.status_code == InputError.code

def test_user_no_perm_in_dm(clear_and_register):
    message = requests.post(config.url + 'message/senddm/v1', json={'token':pytest.user1.json()['token'],'dm_id':pytest.dm1.json()['dm_id'],'message':"Test"})
    requests.post(config.url + 'message/senddm/v1', json={'token':pytest.user1.json()['token'],'dm_id':pytest.dm1.json()['dm_id'],'message':"Tesdsdsdst"})
    requests.post(config.url + 'message/pin/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id']})
    resp = requests.post(config.url + 'message/unpin/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id']})
    assert resp.status_code == AccessError.code

def test_standard_dm(clear_and_register):
    message =  requests.post(config.url + 'message/senddm/v1', json={'token':pytest.user1.json()['token'],'dm_id':pytest.dm1.json()['dm_id'],'message':"Test"})
    requests.post(config.url + 'message/pin/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id']})
    resp = requests.post(config.url + 'message/unpin/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id']})
    assert resp.status_code == 200

def test_invalid_message_id(clear_and_register):
    resp = requests.post(config.url + 'message/unpin/v1', json={'token': pytest.user1.json()['token'], 'message_id': 0})
    assert resp.status_code == InputError.code

def test_not_pinned(clear_and_register):
    message = requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Test"})
    resp = requests.post(config.url + 'message/unpin/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id']})
    assert resp.status_code == InputError.code

def test_pin_didnt_post(clear_and_register):
    requests.post(config.url + 'channel/join/v2', json={'token': pytest.user2.json()['token'], 'channel_id': pytest.channel1.json()['channel_id']})
    message = requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Test"})
    requests.post(config.url + 'message/pin/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id']})
    resp = requests.post(config.url + 'message/unpin/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id']})
    assert resp.status_code == AccessError.code