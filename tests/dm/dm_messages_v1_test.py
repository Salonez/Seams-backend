import pytest
import requests
import json
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
    pytest.u_id1 = [pytest.user1.json()['auth_user_id'], pytest.user2.json()['auth_user_id'], pytest.user3.json()['auth_user_id']]
    pytest.u_id2 = [pytest.user1.json()['auth_user_id']]    
    pytest.dm1 = requests.post(config.url + 'dm/create/v1', 
        json={'token':pytest.creator.json()['token'], 
                'u_ids': pytest.u_id1})
    pytest.dm2 = requests.post(config.url + 'dm/create/v1', 
        json={'token':pytest.creator.json()['token'], 
                'u_ids': pytest.u_id2})

def test_invalid_user(clear_and_register):
    resp = requests.get(config.url + 'dm/messages/v1', params={'token':'dodytoken', 'dm_id': pytest.dm1.json()['dm_id'], 'start': 0})
    assert (resp.status_code == 403)

def test_invalid_dm_id(clear_and_register):
    resp = requests.get(config.url + 'dm/messages/v1', params={'token':pytest.creator.json()['token'], 'dm_id': 34567, 'start': 0})
    assert (resp.status_code == 400)

def test_not_a_member(clear_and_register):
    resp = requests.get(config.url + 'dm/messages/v1', params={'token':pytest.user3.json()['token'], 'dm_id': pytest.dm2.json()['dm_id'], 'start': 0}) 
    assert (resp.status_code == 403)

def test_start_too_big(clear_and_register):
    resp = requests.get(config.url + 'dm/messages/v1', params={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'start': 45678})
    assert resp.status_code == 400

def test_working_dm_messages(clear_and_register):
    resp = requests.get(config.url + 'dm/messages/v1', params={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'start': 0})
    response_data = resp.json()
    
    assert response_data == {
        'messages': [], 
        'start': 0,
        'end': -1 
    }