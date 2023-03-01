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
    return

def test_invalid_message_id(clear_and_register):
    message =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Test"})
    requests.post(config.url + 'message/react/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'react_id': 1})
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': pytest.user1.json()['token'], 'message_id': 0, 'react_id': 1})
    assert resp.status_code == InputError.code

def test_invalid_react_id(clear_and_register):
    message =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Test"})
    requests.post(config.url + 'message/react/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'react_id': 1})
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'react_id': 0})
    assert resp.status_code == InputError.code

def test_no_react(clear_and_register):
    message =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Test"})
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'react_id': 1})
    assert resp.status_code == InputError.code

def test_normal_function(clear_and_register):
    message =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Test"})
    requests.post(config.url + 'message/react/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'react_id': 1})
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'react_id': 1})
    assert resp.status_code == 200

def test_not_member(clear_and_register):
    message =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Test"})
    requests.post(config.url + 'message/react/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'react_id': 1})
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id'], 'react_id': 1})
    assert resp.status_code == InputError.code

def test_coverage(clear_and_register):
    requests.post(config.url + 'channel/join/v2', json={'token': pytest.user2.json()['token'], 'channel_id': pytest.channel1.json()['channel_id']})
    message =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Test"})
    message2 =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user2.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Test"})
    requests.post(config.url + 'message/react/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'react_id': 1})
    requests.post(config.url + 'message/react/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id'], 'react_id': 1})
    requests.post(config.url + 'message/react/v1', json={'token': pytest.user2.json()['token'], 'message_id': message2.json()['message_id'], 'react_id': 1})
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id'], 'react_id': 1})
    assert resp.status_code == 200