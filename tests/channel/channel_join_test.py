import pytest
import requests
import json
from src import config

from src.error import *


# Given a channel_id of a channel that the authorised user can join, adds them to that channel.

# Parameters:{ auth_user_id, channel_id }Return Type:{}

# InputError when any of:
      
#         channel_id does not refer to a valid channel
#         the authorised user is already a member of the channel
      
# AccessError when:
      
#         channel_id refers to a channel that is private and the authorised user is not already a channel member and is not a global owner

# @pytest.fixture


user_id = 1
user_id2 = 2
# owner_user_id = 100
public_channel_id = 1
private_channel_id = 2

@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')
    pytest.user1 = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    pytest.user2 = requests.post(config.url + 'auth/register/v2', json={'email': 'testadmin@test.com', 'password': 'password', 'name_first': 'Nicholas', 'name_last': 'Decsease'})
    pytest.user3 = requests.post(config.url + 'auth/register/v2', json={'email': 'regular@gmail.com', 'password': 'password', 'name_first': 'Nicholas', 'name_last': 'Decsease'})
    pytest.channel1 = requests.post(config.url + 'channels/create/v2', json={'token': pytest.user2.json()['token'], 'name': 'testchannel', 'is_public': True})
    pytest.channel2 = requests.post(config.url + 'channels/create/v2', json={'token': pytest.user2.json()['token'], 'name': 'testchannel2', 'is_public': False})
    return

def test_join_public_channel(clear_and_register):
    requests.post(config.url + 'channel/join/v2', json={'token': pytest.user3.json()['token'], 'channel_id': pytest.channel1.json()['channel_id']})
    channels = requests.get(config.url + 'channels/list/v2', params={'token': pytest.user3.json()['token']})
    print (channels.json()['channels'])
    for channel in channels.json()['channels']:
        assert channel['channel_id'] == pytest.channel1.json()['channel_id']

def test_invalid_channel(clear_and_register):
    resp = requests.post(config.url + 'channel/join/v2', json={'token': pytest.user3.json()['token'], 'channel_id': 0})
    assert resp.status_code == 400

def test_invalid_user(clear_and_register):
    resp = requests.post(config.url + 'channel/join/v2', json={'token': 0, 'channel_id': pytest.channel1.json()['channel_id']})
    assert resp.status_code == 403

def test_already_in_channel(clear_and_register):
    requests.post(config.url + 'channel/join/v2', json={'token': pytest.user3.json()['token'], 'channel_id': pytest.channel1.json()['channel_id']})
    resp = requests.post(config.url + 'channel/join/v2', json={'token': pytest.user3.json()['token'], 'channel_id': pytest.channel1.json()['channel_id']})
    assert resp.status_code == 400

def test_channel_private_not_member(clear_and_register):
    resp = requests.post(config.url + 'channel/join/v2', json={'token': pytest.user3.json()['token'], 'channel_id': pytest.channel2.json()['channel_id']})
    assert resp.status_code == 403

def test_gloabl_owner(clear_and_register):
    resp = requests.post(config.url + 'channel/join/v2', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel2.json()['channel_id']})
    assert resp.status_code == 200

def test_cannot_join_channel_you_created(clear_and_register):
    resp = requests.post(config.url + 'channel/join/v2', json={'token': pytest.user2.json()['token'], 'channel_id': pytest.channel2.json()['channel_id']})
    assert resp.status_code == 400
# def test_variety_join_and_invite(clear_and_register):
#     channel_join_v1(user_id, public_channel_id)
#     channel_invite_v1(user_id2, private_channel_id, user_id)
#     channels = channels_list_v1(user_id)
#     joined_channel_list = []
#     for channel in channels['channels']:
#         joined_channel_list.append(channel['channel_id'])
#     assert joined_channel_list == [public_channel_id,private_channel_id]



# def test_channel_join_v1_output_type(clear_and_register):
#     # Test and see if the response variables have the appropriate types
#     output = channel_join_v1(user_id, public_channel_id)

#     # Check if its an dictionary
#     assert isinstance(output, dict)

#     # Check if the dictionary is empty
#     assert not bool(output)
