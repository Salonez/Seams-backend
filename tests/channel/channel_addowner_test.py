import pytest
from src.error import *
import requests
import json
from src import config
from tests.helpers import clear

@pytest.fixture
def global_own():
    clear()
    global_owner = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cover', 'name_last': 'Age'})
    requests.post(config.url + 'channels/create/v2', json={'token': global_owner.json()['token'], 'name': 'Coverage channel', 'is_public': True})
    return global_owner

def test_valid_addowner(global_own):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': owner.json()['token'], 'name': 'TestChannel', 'is_public': True})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    requests.post(config.url + 'channel/join/v2', json={'token': member.json()['token'], 'channel_id': channel.json()['channel_id']})
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': owner.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': member.json()['auth_user_id']})
    assert resp.status_code == 200
    resp = requests.get(config.url + 'channel/details/v2', params={'token': owner.json()['token'], 'channel_id': channel.json()['channel_id']})
    found_in_owners = False
    for owners in resp.json()['owner_members']:
        if member.json()['auth_user_id'] == owners['u_id']:
            found_in_owners = True
    assert found_in_owners is True

def test_invalid_channel_id(global_own):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    invalid_channel_id = 9999
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': owner.json()['token'], 'channel_id': invalid_channel_id, 'u_id': member.json()['auth_user_id']})
    assert resp.status_code == 400

def test_invalid_u_id(global_own):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': owner.json()['token'], 'name': 'TestChannel', 'is_public': True})
    invalid_u_id = 9999
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': owner.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': invalid_u_id})
    assert resp.status_code == 400

def test_non_member_of_channel(global_own):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': owner.json()['token'], 'name': 'TestChannel', 'is_public': True})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': owner.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': member.json()['auth_user_id']})
    assert resp.status_code == 400

def test_already_owner(global_own):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': owner.json()['token'], 'name': 'TestChannel', 'is_public': True})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    requests.post(config.url + 'channel/join/v2', json={'token': member.json()['token'], 'channel_id': channel.json()['channel_id']})
    requests.post(config.url + 'channel/addowner/v1', json={'token': owner.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': member.json()['auth_user_id']})
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': owner.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': member.json()['auth_user_id']})
    assert resp.status_code == 400

def test_non_owner_attempts_to_add(global_own):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': owner.json()['token'], 'name': 'TestChannel', 'is_public': True})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    requests.post(config.url + 'channel/join/v2', json={'token': member.json()['token'], 'channel_id': channel.json()['channel_id']})
    fake_owner = requests.post(config.url + 'auth/register/v2', json={'email': 'fake@gmail.com', 'password': '1234567', 'name_first': 'Fakie', 'name_last': 'Fake'})
    requests.post(config.url + 'channel/join/v2', json={'token': fake_owner.json()['token'], 'channel_id': channel.json()['channel_id']})
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': fake_owner.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': member.json()['auth_user_id']})
    assert resp.status_code == 403

def test_non_member_cannot_add_himself_as_owner(global_own):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    woodys_public_toybox = requests.post(config.url + 'channels/create/v2', json={'token': owner.json()['token'], 'name': 'woodys toybox', 'is_public': True})
    user_buzz = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'buzz', 'name_last': 'lightyear'})
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': user_buzz.json()['token'], 'channel_id': woodys_public_toybox.json()['channel_id'], 'u_id': user_buzz.json()['auth_user_id']})
    assert resp.status_code == 403

def test_global_owner_member_can_addowner(global_own):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    woodys_public_toybox = requests.post(config.url + 'channels/create/v2', json={'token': owner.json()['token'], 'name': 'woodys toybox', 'is_public': True})
    member = requests.post(config.url + 'auth/register/v2', json={'email': '123amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    requests.post(config.url + 'channel/join/v2', json={'token': member.json()['token'], 'channel_id': woodys_public_toybox.json()['channel_id']})
    requests.post(config.url + 'channel/join/v2', json={'token': global_own.json()['token'], 'channel_id': woodys_public_toybox.json()['channel_id']})
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': global_own.json()['token'], 'channel_id': woodys_public_toybox.json()['channel_id'], 'u_id': member.json()['auth_user_id']})
    assert resp.status_code == 200

def test_global_owner_non_member_cant_addowner_public(global_own):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    woodys_public_toybox = requests.post(config.url + 'channels/create/v2', json={'token': owner.json()['token'], 'name': 'woodys toybox', 'is_public': True})
    member = requests.post(config.url + 'auth/register/v2', json={'email': '123amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    requests.post(config.url + 'channel/join/v2', json={'token': member.json()['token'], 'channel_id': woodys_public_toybox.json()['channel_id']})
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': global_own.json()['token'], 'channel_id': woodys_public_toybox.json()['channel_id'], 'u_id': member.json()['auth_user_id']})
    assert resp.status_code == 403

def test_global_owner_non_member_cant_addowner_private(global_own):
    owner = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    woodys_public_toybox = requests.post(config.url + 'channels/create/v2', json={'token': owner.json()['token'], 'name': 'woodys toybox', 'is_public': False})
    member = requests.post(config.url + 'auth/register/v2', json={'email': '123amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    requests.post(config.url + 'channel/join/v2', json={'token': member.json()['token'], 'channel_id': woodys_public_toybox.json()['channel_id']})
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': global_own.json()['token'], 'channel_id': woodys_public_toybox.json()['channel_id'], 'u_id': member.json()['auth_user_id']})
    assert resp.status_code == 403
