import pytest
import requests
from src import config
from src.error import *
from tests.helpers import clear

@pytest.fixture
def clear_and_register():
    clear()
    requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cover', 'name_last': 'Age'})

def test_valid_create_with_1(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    owner_profile = requests.get(config.url + 'user/profile/v1',params={'u_id': owner.json()['auth_user_id'],'token': owner.json()['token']})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    member_profile = requests.get(config.url + 'user/profile/v1',params={'u_id': member.json()['auth_user_id'],'token': member.json()['token']})
    resp =  requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [member.json()['auth_user_id']]})
    assert resp.status_code == 200
    assert resp.json()['dm_id'] == 1
    dm_detail = requests.get(config.url + 'dm/details/v1', params={'token':owner.json()['token'],'dm_id': 1})
    correct_name = ', '.join(sorted([owner_profile.json()['user']['handle_str'], member_profile.json()['user']['handle_str']]))
    assert dm_detail.json()['name'] == correct_name
    assert owner_profile.json()['user'] in dm_detail.json()['members']
    assert member_profile.json()['user'] in dm_detail.json()['members']

def test_valid_create_with_many(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    owner_profile = requests.get(config.url + 'user/profile/v1',params={'u_id': owner.json()['auth_user_id'],'token': owner.json()['token']})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    member_profile = requests.get(config.url + 'user/profile/v1',params={'u_id': member.json()['auth_user_id'],'token': member.json()['token']})
    member1 = requests.post(config.url + 'auth/register/v2', json={'email': 'google@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Matt'})
    member1_profile = requests.get(config.url + 'user/profile/v1',params={'u_id': member1.json()['auth_user_id'],'token': member1.json()['token']})
    resp =  requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [member.json()['auth_user_id'], member1.json()['auth_user_id']]})
    assert resp.status_code == 200
    assert resp.json()['dm_id'] == 1
    dm_detail = requests.get(config.url + 'dm/details/v1', params={'token':owner.json()['token'],'dm_id': 1})
    correct_name = ', '.join(sorted([owner_profile.json()['user']['handle_str'], member_profile.json()['user']['handle_str'], member1_profile.json()['user']['handle_str']]))
    assert dm_detail.json()['name'] == correct_name
    assert owner_profile.json()['user'] in dm_detail.json()['members']
    assert member_profile.json()['user'] in dm_detail.json()['members']
    assert member_profile.json()['user'] in dm_detail.json()['members']

def test_valid_create_dm_twice(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    owner_profile = requests.get(config.url + 'user/profile/v1',params={'u_id': owner.json()['auth_user_id'],'token': owner.json()['token']})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    member_profile = requests.get(config.url + 'user/profile/v1',params={'u_id': member.json()['auth_user_id'],'token': member.json()['token']})
    requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [member.json()['auth_user_id']]})
    resp =  requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [member.json()['auth_user_id']]})
    assert resp.status_code == 200
    assert resp.json()['dm_id'] == 2
    dm_detail = requests.get(config.url + 'dm/details/v1', params={'token':owner.json()['token'],'dm_id': 2})
    correct_name = ', '.join(sorted([owner_profile.json()['user']['handle_str'], member_profile.json()['user']['handle_str']]))
    assert dm_detail.json()['name'] == correct_name
    assert owner_profile.json()['user'] in dm_detail.json()['members']
    assert member_profile.json()['user'] in dm_detail.json()['members']

def test_invalid_u_id(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    invalid_member_id = 9999
    resp =  requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [invalid_member_id]})
    assert resp.status_code == 400

def test_duplicate_u_id(clear_and_register):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    resp =  requests.post(config.url + 'dm/create/v1', json={'token':owner.json()['token'],'u_ids': [member.json()['auth_user_id'], member.json()['auth_user_id']]})
    assert resp.status_code == 400