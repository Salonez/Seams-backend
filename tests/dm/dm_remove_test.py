import pytest
import requests
from src import config
from src.error import *
from tests.helpers import clear

@pytest.fixture
def clear_and_register():
    clear()
    requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cover', 'name_last': 'Age'})

def test_valid_remove(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [member.json()['auth_user_id']]})
    resp = requests.delete(config.url + 'dm/remove/v1', json={'token':owner.json()['token'],'dm_id': dm1.json()['dm_id']})
    assert resp.status_code == 200
    dm_list = requests.get(config.url + 'dm/list/v1', params={'token':owner.json()['token']})
    assert dm_list.json()['dms'] == []

def test_valid_remove_with_many_dms(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [member.json()['auth_user_id']]})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [member.json()['auth_user_id']]})
    resp = requests.delete(config.url + 'dm/remove/v1', json={'token':owner.json()['token'],'dm_id': dm1.json()['dm_id']})
    assert resp.status_code == 200
    dm_list = requests.get(config.url + 'dm/list/v1', params={'token':owner.json()['token']})
    found_deleted_dm = False
    for dm in dm_list.json()['dms']:
        if dm['dm_id'] == dm1.json()['dm_id']:
            found_deleted_dm = True
    assert found_deleted_dm == False

def test_invalid_dm_id(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    invalid_dm = 9999
    resp = requests.delete(config.url + 'dm/remove/v1', json={'token':owner.json()['token'],'dm_id': invalid_dm})
    assert resp.status_code == 400

def test_owner_no_longer_in_DM(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [member.json()['auth_user_id']]})
    requests.post(config.url + 'dm/leave/v1', json={'token':owner.json()['token'],'dm_id': dm1.json()['dm_id']})
    resp = requests.delete(config.url + 'dm/remove/v1', json={'token':owner.json()['token'],'dm_id': dm1.json()['dm_id']})
    assert resp.status_code == 403

def test_non_creator(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [member.json()['auth_user_id']]})
    resp = requests.delete(config.url + 'dm/remove/v1', json={'token':member.json()['token'],'dm_id': dm1.json()['dm_id']})
    assert resp.status_code == 403