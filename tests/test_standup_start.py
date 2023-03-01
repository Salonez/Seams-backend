import pytest
import requests
import time
from src import config
from src.error import *
from tests.helpers import clear
from src.data_store import data_store


@pytest.fixture
def clear_and_register():
    clear()
    pytest.creator = requests.post(config.url + 'auth/register/v2', 
        json={  'email': 'testemailcreate@gmail.com', 
                'password': 'password', 
                'name_first': 'John', 
                'name_last': 'Sea'})
    pytest.user1 = requests.post(config.url + 'auth/register/v2', 
        json={  'email': 'testemail1@gmail.com', 
                'password': 'password', 
                'name_first': 'Ron', 
                'name_last': 'Swanson'})
    pytest.user2 = requests.post(config.url + 'auth/register/v2', 
        json={  'email': 'testemail2@gmail.com', 
                'password': 'password', 
                'name_first': 'Steve', 
                'name_last': 'Jobs'})
    pytest.user3 = requests.post(config.url + 'auth/register/v2', 
        json={  'email': 'testemail3@gmail.com', 
                'password': 'password', 
                'name_first': 'Bob',
                'name_last': 'Bobson'})
    pytest.channel1 = requests.post(config.url + 'channels/create/v2', 
        json={  'token': pytest.creator.json()['token'], 
                'name': 'something', 
                'is_public' : True})
    pytest.channel2 = requests.post(config.url + 'channels/create/v2', 
        json={  'token': pytest.creator.json()['token'], 
                'name': 'hello', 
                'is_public' : False})
    requests.post(config.url + 'channel/join/v2', 
        json={  'token': pytest.user2.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id']})

def test_invalid_id(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token': -1, 
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    assert (resp.status_code == 403)
    
def test_invalid_channel_id(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'], 
                'channel_id': -1,
                'length': 5})
    assert (resp.status_code == 400)

def test_negative_length(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': -5})
    assert (resp.status_code == 400)

def test_already_active_standup(clear_and_register):
    requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.user2.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    assert (resp.status_code == 400)

def test_not_member_of_channel(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.user1.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    assert (resp.status_code == 403)


def test_creates_standup_public(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    resp_data = resp.json()
    store = data_store.get()
    print(store)
    print(resp_data)
    assert (resp_data.keys() == {'time_finish'})

def test_creates_standup_private(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'], 
                'channel_id': pytest.channel2.json()['channel_id'],
                'length': 5})
    resp_data = resp.json()
    store = data_store.get()
    print(store)
    print(resp_data)
    assert (resp_data.keys() == {'time_finish'})

def test_creates_standup_not_creator(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.user2.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    resp_data = resp.json()
    store = data_store.get()
    print(store)
    print(resp_data)
    assert (resp_data.keys() == {'time_finish'})

def test_standup_added_as_channel_message(clear_and_register):
    requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 0.25})
    requests.post(config.url + 'standup/send/v1',
            json={'token':pytest.user2.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id'],
                'message': 'happy birthday'})
    requests.post(config.url + 'standup/send/v1',
            json={'token':pytest.creator.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id'],
                'message': 'hello'})
    time.sleep(0.5)
    resp = requests.get(config.url + 'channel/messages/v2',
            params={'token':pytest.user2.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id'],
                'start': 0})
    resp_data = resp.json()
    store = data_store.get()
    print(resp_data)
    assert (resp_data['messages'][0]['message'] == 'stevejobs: happy birthday\njohnsea: hello')
    assert (store['standups'] == [])
    