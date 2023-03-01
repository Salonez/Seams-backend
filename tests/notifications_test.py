import pytest
from src.error import *
import requests
import json
from src import config
from tests.helpers import clear
import time

@pytest.fixture
def clear_and_register():
    clear()

def test_no_notifications(clear_and_register):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cover', 'name_last': 'Age'})
    resp = requests.get(config.url + 'notifications/get/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    assert resp.json()['notifications'] == []

def test_added_to_a_channel_and_dm(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': '1coverage@gmail.com', 'password': '1234567', 'name_first': 'Paul', 'name_last': 'Steven'})
    creator_info = requests.get(config.url + 'user/profile/v1', params={'token': creator.json()['token'],'u_id': creator.json()['auth_user_id']})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'Coverage channel', 'is_public': True})
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id']})
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Smith'})
    requests.post(config.url + 'channel/invite/v2', json={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': user.json()['auth_user_id']})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':creator.json()['token'], 'u_ids': [user.json()['auth_user_id']]})
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': creator.json()['token'], 'dm_id': dm1.json()['dm_id']})
    resp = requests.get(config.url + 'notifications/get/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    assert resp.json()['notifications'] == [
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {dm_details.json()['name']}"},
        {'channel_id': channel.json()['channel_id'], 'dm_id': -1, 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {channel_details.json()['name']}"}
    ]

def test_message_react_in_dm_and_channel(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': '1coverage@gmail.com', 'password': '1234567', 'name_first': 'Owner', 'name_last': 'King'})
    creator_info = requests.get(config.url + 'user/profile/v1', params={'token': creator.json()['token'],'u_id': creator.json()['auth_user_id']})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'Daboiz', 'is_public': True})
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id']})
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cult', 'name_last': 'Jefferson'})
    user_info = requests.get(config.url + 'user/profile/v1', params={'token': user.json()['token'],'u_id': user.json()['auth_user_id']})
    requests.post(config.url + 'channel/invite/v2', json={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': user.json()['auth_user_id']})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':creator.json()['token'], 'u_ids': [user.json()['auth_user_id']]})
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': creator.json()['token'], 'dm_id': dm1.json()['dm_id']})
    channel_message = requests.post(config.url + 'message/send/v1', json={'token':user.json()['token'],'channel_id': channel.json()['channel_id'],'message':f"Hello channel dwellers"})
    dm_message = requests.post(config.url + 'message/senddm/v1', json={'token':user.json()['token'],'dm_id': dm1.json()['dm_id'],'message':f"React me up!"})
    resp = requests.post(config.url + 'message/react/v1', json={'token': user.json()['token'], 'message_id': channel_message.json()['message_id'], 'react_id': 1})
    assert resp.status_code == 200
    resp = requests.post(config.url + 'message/react/v1', json={'token': creator.json()['token'], 'message_id': channel_message.json()['message_id'], 'react_id': 1})
    assert resp.status_code == 200
    resp = requests.post(config.url + 'message/react/v1', json={'token': user.json()['token'], 'message_id': dm_message.json()['message_id'], 'react_id': 1})
    assert resp.status_code == 200
    resp = requests.post(config.url + 'message/react/v1', json={'token': creator.json()['token'], 'message_id': dm_message.json()['message_id'], 'react_id': 1})
    assert resp.status_code == 200
    resp = requests.get(config.url + 'notifications/get/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    assert resp.json()['notifications'] == [
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{creator_info.json()['user']['handle_str']} reacted to your message in {dm_details.json()['name']}"},
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{user_info.json()['user']['handle_str']} reacted to your message in {dm_details.json()['name']}"},
        {'channel_id': channel.json()['channel_id'], 'dm_id': -1, 'notification_message': f"{creator_info.json()['user']['handle_str']} reacted to your message in {channel_details.json()['name']}"},
        {'channel_id': channel.json()['channel_id'], 'dm_id': -1, 'notification_message': f"{user_info.json()['user']['handle_str']} reacted to your message in {channel_details.json()['name']}"},
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {dm_details.json()['name']}"},
        {'channel_id': channel.json()['channel_id'], 'dm_id': -1, 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {channel_details.json()['name']}"}
    ]

def test_tagged_in_channel_message_and_dm_message(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': '1coverage@gmail.com', 'password': '1234567', 'name_first': 'Owner', 'name_last': 'King'})
    creator_info = requests.get(config.url + 'user/profile/v1', params={'token': creator.json()['token'],'u_id': creator.json()['auth_user_id']})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'Daboiz', 'is_public': True})
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id']})
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cult', 'name_last': 'Jefferson'})
    user_info = requests.get(config.url + 'user/profile/v1', params={'token': user.json()['token'],'u_id': user.json()['auth_user_id']})
    requests.post(config.url + 'channel/invite/v2', json={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': user.json()['auth_user_id']})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':creator.json()['token'], 'u_ids': [user.json()['auth_user_id']]})
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': creator.json()['token'], 'dm_id': dm1.json()['dm_id']})
    requests.post(config.url + 'message/send/v1', json={'token':creator.json()['token'],'channel_id': channel.json()['channel_id'],'message':f"Hello @{user_info.json()['user']['handle_str']} "})
    requests.post(config.url + 'message/senddm/v1', json={'token':creator.json()['token'],'dm_id': dm1.json()['dm_id'],'message':f"01234567890123456789 @{user_info.json()['user']['handle_str']} "})
    resp = requests.get(config.url + 'notifications/get/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    assert resp.json()['notifications'] == [
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{creator_info.json()['user']['handle_str']} tagged you in {dm_details.json()['name']}: 01234567890123456789"},
        {'channel_id': channel.json()['channel_id'], 'dm_id': -1, 'notification_message': f"{creator_info.json()['user']['handle_str']} tagged you in {channel_details.json()['name']}: Hello @{user_info.json()['user']['handle_str']}"},
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {dm_details.json()['name']}"},
        {'channel_id': channel.json()['channel_id'], 'dm_id': -1, 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {channel_details.json()['name']}"}
    ]
    #here

def test_tagged_in_channel_message_and_dm_message_user_not_member_of(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': '1coverage@gmail.com', 'password': '1234567', 'name_first': 'Cover', 'name_last': 'Age'})
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cover', 'name_last': 'Age'})
    user_info = requests.get(config.url + 'user/profile/v1', params={'token': user.json()['token'],'u_id': user.json()['auth_user_id']})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'Coverage channel', 'is_public': True})
    dm_user = requests.post(config.url + 'auth/register/v2', json={'email': '2coverage@gmail.com', 'password': '1234567', 'name_first': 'Cover', 'name_last': 'Age'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':creator.json()['token'], 'u_ids': [dm_user.json()['auth_user_id']]})
    requests.post(config.url + 'message/send/v1', json={'token':creator.json()['token'],'channel_id': channel.json()['channel_id'],'message':f"Hello @{user_info.json()['user']['handle_str']}"})
    requests.post(config.url + 'message/senddm/v1', json={'token':creator.json()['token'],'dm_id': dm1.json()['dm_id'],'message':f"Hello @{user_info.json()['user']['handle_str']}"})
    resp = requests.get(config.url + 'notifications/get/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    assert resp.json()['notifications'] == []

def test_creator_dm_tags_himself_twice_and_tag_mistake_for_user(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': '1coverage@gmail.com', 'password': '1234567', 'name_first': 'Owner', 'name_last': 'Brando'})
    creator_info = requests.get(config.url + 'user/profile/v1', params={'token': creator.json()['token'],'u_id': creator.json()['auth_user_id']})
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Lamelo', 'name_last': 'Ball'})
    user_info = requests.get(config.url + 'user/profile/v1', params={'token': user.json()['token'],'u_id': user.json()['auth_user_id']})
    dm_user = requests.post(config.url + 'auth/register/v2', json={'email': 'jojo@gmail.com', 'password': '1234567', 'name_first': 'Jonathan', 'name_last': 'Joestar'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':creator.json()['token'], 'u_ids': [user.json()['auth_user_id'], dm_user.json()['auth_user_id']]})
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': creator.json()['token'], 'dm_id': dm1.json()['dm_id']})
    requests.post(config.url + 'message/senddm/v1', json={'token':creator.json()['token'],'dm_id': dm1.json()['dm_id'],'message':f"01234567890123456789@{creator_info.json()['user']['handle_str']}@{creator_info.json()['user']['handle_str']}@{user_info.json()['user']['handle_str']}1"})
    resp = requests.get(config.url + 'notifications/get/v1', params={'token': creator.json()['token']})
    assert resp.status_code == 200
    assert resp.json()['notifications'] == [
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{creator_info.json()['user']['handle_str']} tagged you in {dm_details.json()['name']}: 01234567890123456789"},
    ]
    resp = requests.get(config.url + 'notifications/get/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    assert resp.json()['notifications'] == [
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {dm_details.json()['name']}"},
    ]

def test_just_tag_(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': '1coverage@gmail.com', 'password': '1234567', 'name_first': 'Owner', 'name_last': 'King'})
    creator_info = requests.get(config.url + 'user/profile/v1', params={'token': creator.json()['token'],'u_id': creator.json()['auth_user_id']})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'Daboiz', 'is_public': True})
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id']})
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cult', 'name_last': 'Jefferson'})
    user_info = requests.get(config.url + 'user/profile/v1', params={'token': user.json()['token'],'u_id': user.json()['auth_user_id']})
    requests.post(config.url + 'channel/invite/v2', json={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': user.json()['auth_user_id']})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':creator.json()['token'], 'u_ids': [user.json()['auth_user_id']]})
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': creator.json()['token'], 'dm_id': dm1.json()['dm_id']})
    requests.post(config.url + 'message/send/v1', json={'token':creator.json()['token'],'channel_id': channel.json()['channel_id'],'message':f"@{user_info.json()['user']['handle_str']}"})
    requests.post(config.url + 'message/senddm/v1', json={'token':creator.json()['token'],'dm_id': dm1.json()['dm_id'],'message':f"@{user_info.json()['user']['handle_str']}"})
    resp = requests.get(config.url + 'notifications/get/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    assert resp.json()['notifications'] == [
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{creator_info.json()['user']['handle_str']} tagged you in {dm_details.json()['name']}: @{user_info.json()['user']['handle_str']}"},
        {'channel_id': channel.json()['channel_id'], 'dm_id': -1, 'notification_message': f"{creator_info.json()['user']['handle_str']} tagged you in {channel_details.json()['name']}: @{user_info.json()['user']['handle_str']}"},
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {dm_details.json()['name']}"},
        {'channel_id': channel.json()['channel_id'], 'dm_id': -1, 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {channel_details.json()['name']}"}
    ]

def test_reacted_message_user_not_in_channel(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': '1coverage@gmail.com', 'password': '1234567', 'name_first': 'Owner', 'name_last': 'King'})
    creator_info = requests.get(config.url + 'user/profile/v1', params={'token': creator.json()['token'],'u_id': creator.json()['auth_user_id']})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'Daboiz', 'is_public': True})
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id']})
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cult', 'name_last': 'Jefferson'})
    requests.post(config.url + 'channel/invite/v2', json={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': user.json()['auth_user_id']})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':creator.json()['token'], 'u_ids': [user.json()['auth_user_id']]})
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': creator.json()['token'], 'dm_id': dm1.json()['dm_id']})
    channel_message = requests.post(config.url + 'message/send/v1', json={'token':user.json()['token'],'channel_id': channel.json()['channel_id'],'message':f"Hello channel dwellers"})
    dm_message = requests.post(config.url + 'message/senddm/v1', json={'token':user.json()['token'],'dm_id': dm1.json()['dm_id'],'message':f"React me up!"})
    requests.post(config.url + 'channel/leave/v1', json={'token': user.json()['token'], 'channel_id': channel.json()['channel_id']})
    requests.post(config.url + 'dm/leave/v1', json={'token': user.json()['token'], 'dm_id': dm1.json()['dm_id']})
    resp = requests.post(config.url + 'message/react/v1', json={'token': user.json()['token'], 'message_id': channel_message.json()['message_id'], 'react_id': 1})
    resp = requests.post(config.url + 'message/react/v1', json={'token': creator.json()['token'], 'message_id': channel_message.json()['message_id'], 'react_id': 1})
    resp = requests.post(config.url + 'message/react/v1', json={'token': user.json()['token'], 'message_id': dm_message.json()['message_id'], 'react_id': 1})
    resp = requests.post(config.url + 'message/react/v1', json={'token': creator.json()['token'], 'message_id': dm_message.json()['message_id'], 'react_id': 1})
    resp = requests.get(config.url + 'notifications/get/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    assert resp.json()['notifications'] == [
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {dm_details.json()['name']}"},
        {'channel_id': channel.json()['channel_id'], 'dm_id': -1, 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {channel_details.json()['name']}"}
    ]

def test_sendlater(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': '1coverage@gmail.com', 'password': '1234567', 'name_first': 'Owner', 'name_last': 'King'})
    creator_info = requests.get(config.url + 'user/profile/v1', params={'token': creator.json()['token'],'u_id': creator.json()['auth_user_id']})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'Daboiz', 'is_public': True})
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id']})
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cult', 'name_last': 'Jefferson'})
    user_info = requests.get(config.url + 'user/profile/v1', params={'token': user.json()['token'],'u_id': user.json()['auth_user_id']})
    requests.post(config.url + 'channel/invite/v2', json={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': user.json()['auth_user_id']})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':creator.json()['token'], 'u_ids': [user.json()['auth_user_id']]})
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': creator.json()['token'], 'dm_id': dm1.json()['dm_id']})
    requests.post(config.url + 'message/sendlater/v1', json={'token':creator.json()['token'],'channel_id':channel.json()['channel_id'],'message': f"Hello @{user_info.json()['user']['handle_str']}", 'time_sent': int(time.time())+0.25 })
    requests.post(config.url + 'message/sendlaterdm/v1', json={'token':creator.json()['token'],'dm_id':dm1.json()['dm_id'],'message':f"01234567890123456789 @{user_info.json()['user']['handle_str']} ", 'time_sent': int(time.time())+0.25 })
    time.sleep(2)
    resp = requests.get(config.url + 'notifications/get/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    assert resp.json()['notifications'] == [
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{creator_info.json()['user']['handle_str']} tagged you in {dm_details.json()['name']}: 01234567890123456789"},
        {'channel_id': channel.json()['channel_id'], 'dm_id': -1, 'notification_message': f"{creator_info.json()['user']['handle_str']} tagged you in {channel_details.json()['name']}: Hello @{user_info.json()['user']['handle_str']}"},
        {'channel_id': -1, 'dm_id': dm1.json()['dm_id'], 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {dm_details.json()['name']}"},
        {'channel_id': channel.json()['channel_id'], 'dm_id': -1, 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {channel_details.json()['name']}"}
    ]

def test_standup_messages(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': '1coverage@gmail.com', 'password': '1234567', 'name_first': 'Owner', 'name_last': 'King'})
    creator_info = requests.get(config.url + 'user/profile/v1', params={'token': creator.json()['token'],'u_id': creator.json()['auth_user_id']})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'Daboiz', 'is_public': True})
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id']})
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cult', 'name_last': 'Jefferson'})
    user_info = requests.get(config.url + 'user/profile/v1', params={'token': user.json()['token'],'u_id': user.json()['auth_user_id']})
    requests.post(config.url + 'channel/invite/v2', json={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': user.json()['auth_user_id']})
    requests.post(config.url + 'standup/start/v1', json={  'token':creator.json()['token'], 'channel_id': channel.json()['channel_id'],'length': 0.25})
    requests.post(config.url + 'standup/send/v1',json={'token':creator.json()['token'], 'channel_id': channel.json()['channel_id'],'message':f"@{user_info.json()['user']['handle_str']}"})
    time.sleep(1)
    resp = requests.get(config.url + 'notifications/get/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    assert resp.json()['notifications'] == [
        {'channel_id': channel.json()['channel_id'], 'dm_id': -1, 'notification_message': f"{creator_info.json()['user']['handle_str']} added you to {channel_details.json()['name']}"}
    ]