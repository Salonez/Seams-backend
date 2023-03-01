import pytest
import requests
from src import config
from src.error import *
from tests.helpers import clear

@pytest.fixture
def clear_and_register():
    clear()
    requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cover', 'name_last': 'Age'})

def test_1_dm_in_list(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    owner_profile = requests.get(config.url + 'user/profile/v1',params={'u_id': owner.json()['auth_user_id'],'token': owner.json()['token']})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    member_profile = requests.get(config.url + 'user/profile/v1',params={'u_id': member.json()['auth_user_id'],'token': member.json()['token']})
    requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [member.json()['auth_user_id']]})
    resp = requests.get(config.url + 'dm/list/v1', params={'token':owner.json()['token']})
    assert resp.status_code == 200
    correct_name = ', '.join(sorted([owner_profile.json()['user']['handle_str'], member_profile.json()['user']['handle_str']]))
    dm_found = False
    for dm in resp.json()['dms']:
        if dm['dm_id'] == 1:
            dm_found = True
            assert dm['name'] == correct_name
    assert dm_found == True

def test_no_dm_in_list(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    resp = requests.get(config.url + 'dm/list/v1', params={'token':owner.json()['token']})
    assert resp.status_code == 200
    assert resp.json()['dms'] == []

def test_many_dm_in_list(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    owner_profile = requests.get(config.url + 'user/profile/v1',params={'u_id': owner.json()['auth_user_id'],'token': owner.json()['token']})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    member_profile = requests.get(config.url + 'user/profile/v1',params={'u_id': member.json()['auth_user_id'],'token': member.json()['token']})
    requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [member.json()['auth_user_id']]})
    owner1 = requests.post(config.url + 'auth/register/v2', json={'email': 'copy@gmail.com', 'password': '1234567', 'name_first': 'Jonah', 'name_last': 'Mellow'})
    owner1_profile = requests.get(config.url + 'user/profile/v1',params={'u_id': owner1.json()['auth_user_id'],'token': owner1.json()['token']})
    requests.post(config.url + 'dm/create/v1', json={'token':owner1.json()['token'],'u_ids': [owner.json()['auth_user_id'], member.json()['auth_user_id']]})
    resp = requests.get(config.url + 'dm/list/v1', params={'token':owner.json()['token']})
    assert resp.status_code == 200
    correct_name = ', '.join(sorted([owner_profile.json()['user']['handle_str'], member_profile.json()['user']['handle_str']]))
    correct_name1 = ', '.join(sorted([owner1_profile.json()['user']['handle_str'], owner_profile.json()['user']['handle_str'], member_profile.json()['user']['handle_str']]))
    dm_found = False
    dm_found1 = False
    for dm in resp.json()['dms']:
        if dm['dm_id'] == 1:
            dm_found = True
            assert dm['name'] == correct_name
        if dm['dm_id'] == 2:
            dm_found1 = True
            assert dm['name'] == correct_name1
    assert dm_found == True
    assert dm_found1 == True