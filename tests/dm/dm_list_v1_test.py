import pytest
import requests
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
    pytest.user4 = requests.post(config.url + 'auth/register/v2', 
        json={  'email': 'skdjbr@gmail.com', 
                'password': 'password', 
                'name_first': 'vkjs', 
                'name_last': 'sjdn'})
    pytest.u_id1 = [pytest.user1.json()['auth_user_id'], pytest.user2.json()['auth_user_id'], pytest.user3.json()['auth_user_id']]
    pytest.u_id2 = [pytest.user1.json()['auth_user_id']]    
    pytest.dm1 = requests.post(config.url + 'dm/create/v1', 
        json={'token':pytest.creator.json()['token'], 
                'u_ids': pytest.u_id1})
    pytest.dm2 = requests.post(config.url + 'dm/create/v1', 
        json={'token':pytest.creator.json()['token'], 
                'u_ids': pytest.u_id2})


def test_invalid_user(clear_and_register):
    resp = requests.get(config.url + 'dm/list/v1', params={'token': 'dodgytoken'})
    assert (resp.status_code == 403)
    
def test_user_in_2_channels(clear_and_register):
    resp = requests.get(config.url + 'dm/list/v1', params={'token':pytest.user1.json()['token']})
    response_data = resp.json()
    assert (resp.status_code == 200)
    assert (response_data.keys() == {'dms'})
    assert (len(response_data['dms']) == 2)
    
def test_user_in_1_channels(clear_and_register):
    resp = requests.get(config.url + 'dm/list/v1', params={'token':pytest.user2.json()['token']})
    response_data = resp.json()
    assert (resp.status_code == 200)
    assert (response_data.keys() == {'dms'})
    assert (len(response_data['dms']) == 1)

def test_user_in_no_channels(clear_and_register):
    resp = requests.get(config.url + 'dm/list/v1', params={'token':pytest.user4.json()['token']})
    response_data = resp.json()
    assert (resp.status_code == 200)
    assert (response_data.keys() == {'dms'})
    assert (len(response_data['dms']) == 0)