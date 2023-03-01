import pytest
import requests
import json
from src.error import *
from src import config

@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')
    pytest.user1 = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    pytest.user2 = requests.post(config.url + 'auth/register/v2', json={'email': 'testadmin@test.com', 'password': 'password', 'name_first': 'Nicholas', 'name_last': 'Decsease'})
    pytest.channel1 = requests.post(config.url + 'channels/create/v2', json={'token': pytest.user1.json()['token'], 'name': 'testchannel', 'is_public': True})
    pytest.channel2 = requests.post(config.url + 'channels/create/v2', json={'token': pytest.user2.json()['token'], 'name': 'testchannel2', 'is_public': False})
    return

def test_channel_messages_normal(clear_and_register):
    resp = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'start': 0})
    assert json.loads(resp.text) == {
        'messages': [], 
        'start': 0,
        'end': -1 
    }

def test_invalid_channel(clear_and_register):
    resp = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': 0, 'start': 0})
    assert resp.status_code == 400

def test_invalid_user(clear_and_register):
    resp = requests.get(config.url + 'channel/messages/v2', params={'token': 0, 'channel_id': pytest.channel1.json()['channel_id'], 'start': 0})
    assert resp.status_code == 403

def test_start_too_large(clear_and_register):
    resp = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'start': 1000})
    assert resp.status_code == 400

def test_start_too_large2(clear_and_register):
    resp = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'start': 1})
    assert resp.status_code == 400

def test_not_in_channel(clear_and_register):
    resp = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel2.json()['channel_id'], 'start': 0})
    assert resp.status_code == 403

def test_user_and_channel_id_wrong(clear_and_register):
    resp = requests.get(config.url + 'channel/messages/v2', params={'token': 0, 'channel_id': 0, 'start': 0})
    assert resp.status_code == 403

def test_pagination(clear_and_register):
    for i in range(124):
        requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': f"{i}"})
    resp = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'start': 0})
    resp2 = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'start': 50})
    resp3 = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'start': 100})
    # print(resp.json())
    
    # json_object = json.loads(resp.json())

    # json_formatted_str = json.dumps(resp3.json(), indent=2)

    # print(json_formatted_str)
    # print(len(resp3.json()['messages']))

    assert resp.json()['start'] == 0 and resp.json()['end'] == 50
    assert resp2.json()['start'] == 50 and resp2.json()['end'] == 100
    assert resp3.json()['start'] == 100 and resp3.json()['end'] == -1