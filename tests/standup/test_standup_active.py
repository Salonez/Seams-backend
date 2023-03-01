import pytest
import requests
from src.data_store import data_store
from src import config
from src.error import *
from tests.helpers import clear


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
                'name': 'something', 
                'is_public' : False})
    requests.post(config.url + 'channel/join/v2', 
        json={  'token': pytest.user2.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id']})
    requests.post(config.url + 'standup/start/v1',
        json={  'token':pytest.creator.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})

def test_invalid_id(clear_and_register):
    resp = requests.get(config.url + 'standup/active/v1',
            params={'token': -1, 
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    assert (resp.status_code == 403)
    
def test_invalid_channel_id(clear_and_register):
    resp = requests.get(config.url + 'standup/active/v1',
            params={'token':pytest.creator.json()['token'], 
                'channel_id': -1})
    assert resp.status_code == 400

def test_not_member_of_channel(clear_and_register):
    resp = requests.get(config.url + 'standup/active/v1',
            params={'token':pytest.user1.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id']})
    assert resp.status_code == 403

def test_active_standup(clear_and_register):
    resp = requests.get(config.url + 'standup/active/v1',
            params={'token':pytest.creator.json()['token'], 
                'channel_id': pytest.channel1.json()['channel_id']})
    resp_data = resp.json()
    store = data_store.get()
    print(store)
    print(resp_data)
    assert (resp_data.keys() == {'is_active', 'time_finish'})
    assert (resp_data['is_active'] == True)
    assert isinstance(resp_data['time_finish'], float)

def test_no_active_standup(clear_and_register):
    resp = requests.get(config.url + 'standup/active/v1',
            params={'token':pytest.creator.json()['token'], 
                'channel_id': pytest.channel2.json()['channel_id']})
    resp_data = resp.json()
    store = data_store.get()
    print(store)
    print(resp_data)
    assert (resp_data.keys() == {'is_active', 'time_finish'})
    assert (resp_data['is_active'] == False)
    assert (resp_data['time_finish'] == None)


