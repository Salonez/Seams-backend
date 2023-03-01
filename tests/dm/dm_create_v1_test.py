import pytest
import requests
from src import config
from src.error import *
from tests.helpers import clear

#These are all for DM create

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
    pytest.u_id = [pytest.user1.json()['auth_user_id'], pytest.user2.json()['auth_user_id'], pytest.user3.json()['auth_user_id']]

		
def test_duplicate_user_error(clear_and_register):
    
    pytest.u_id.append(pytest.user1.json()['auth_user_id'])
    print(pytest.u_id)
    resp =  requests.post(config.url + 'dm/create/v1', 
        json={'token':pytest.creator.json()['token'], 
                'u_ids': pytest.u_id})
    assert (resp.status_code == 400)
    
def test_invalid_user(clear_and_register):
    pytest.u_id.append(234567890)
    resp = requests.post(config.url + 'dm/create/v1', 
        json={  'token':pytest.creator.json()['token'], 
                'u_ids': pytest.u_id})
    assert (resp.status_code == 400)
		
def test_works(clear_and_register):
    resp = requests.post(config.url + 'dm/create/v1', 
        json={'token':pytest.creator.json()['token'], 
                'u_ids': pytest.u_id})
    resp_data = resp.json()
    assert(resp.status_code == 200)
    assert(resp_data.keys() == {'dm_id'})
    assert(resp_data['dm_id'] == 1)