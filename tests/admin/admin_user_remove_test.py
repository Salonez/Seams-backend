import requests
import pytest

from src.channels import channels_create_v1
from tests.helpers import clear
from src.config import url
from src.data_store import data_store


USER1_PAYLOAD = {
    "email": "testemail@email.com",
    "password": "password123",
    "name_first": "Steve",
    "name_last": "Jobs"
}

USER2_PAYLOAD = {
    "email": "testemail2@email.com",
    "password": "password123",
    "name_first": "Bill",
    "name_last": "Gates",
    "handle_str": "billgates"
}

@pytest.fixture
def clear_and_register():
    clear()
    pytest.user1 = requests.post(
        url + 'auth/register/v2',
        json=USER1_PAYLOAD
    ).json()

    pytest.user2 = requests.post(
        url + 'auth/register/v2',
        json=USER2_PAYLOAD
    ).json()


def test_admin_user_remove_v1_invalid_user(clear_and_register):

    resp = requests.delete(
        url + 'admin/user/remove/v1',
        json={
            "token": pytest.user1['token'],
            "u_id": 3
        }
    )

    assert resp.status_code == 400

    # TODO: Test deleted user id


def test_admin_user_remove_v1_remove_only_global_owner(clear_and_register):

    # Global Owner demote self
    resp = requests.delete(
        url + 'admin/user/remove/v1',
        json={
            "token": pytest.user1['token'],
            "u_id": pytest.user1['auth_user_id']
        }
    )

    assert resp.status_code == 400


def test_admin_user_remove_v1_authorised_user_is_not_global_owner(clear_and_register):
    # User 2 (normal user) tries to delete User 1 (Global Owner)
    resp = requests.delete(
        url + 'admin/user/remove/v1',
        json={
            "token": pytest.user2['token'],
            "u_id": pytest.user1['auth_user_id']
        }
    )

    assert resp.status_code == 403


def test_admin_user_remove_v1_successful(clear_and_register):
    # Objective is to remove user 2

    # Create 2 channels, where user 1 is owner for channel 1 and 2 TODO: Convert to HTTP once ready
    requests.post(
        url + 'channels/create/v2',
        json={
            "token": pytest.user1['token'],
            "name": 'TestChannel1',
            "is_public": True 
        }
    )
    requests.post(
        url + 'channels/create/v2',
        json={
            "token": pytest.user1['token'],
            "name": 'TestChannel2',
            "is_public": True 
        }
    )

    # Create 2 channels, where user 2 is owner for channel 3 and 4
    # channels_create_v1(pytest.user2['auth_user_id'], 'TestChannel3', True)
    requests.post(
        url + 'channels/create/v2',
        json={
            "token": pytest.user2['token'],
            "name": 'TestChannel3',
            "is_public": True 
        }
    )
    # channels_create_v1(pytest.user2['auth_user_id'], 'TestChannel4', True)
    requests.post(
        url + 'channels/create/v2',
        json={
            "token": pytest.user2['token'],
            "name": 'TestChannel4',
            "is_public": True 
        }
    )

    # channels_create_v1(pytest.user1['auth_user_id'], 'TestChannel5', True)
    requests.post(
        url + 'channels/create/v2',
        json={
            "token": pytest.user1['token'],
            "name": 'TestChannel5',
            "is_public": True 
        }
    )

    # User 2 join Channel 1 and 2
    requests.post(
        url + 'channel/join/v2',
        json={
            "token": pytest.user2['token'],
            "channel_id": 1
        }
    )
    requests.post(
        url + 'channel/join/v2',
        json={
            "token": pytest.user2['token'],
            "channel_id": 2
        }
    )

    # User 1 join Channel 3 and 4
    requests.post(
        url + 'channel/join/v2',
        json={
            "token": pytest.user1['token'],
            "channel_id": 3
        }
    )
    requests.post(
        url + 'channel/join/v2',
        json={
            "token": pytest.user1['token'],
            "channel_id": 4
        }
    )

    # Both user send 2 messages each
    requests.post(
        url + 'message/send/v1',
        json={
            "token": pytest.user1['token'],
            "channel_id": 1,
            "message": "TestMessage1"
        }
    )
    requests.post(
        url + 'message/send/v1',
        json={
            "token": pytest.user2['token'],
            "channel_id": 1,
            "message": "TestMessage2"
        }
    )

    requests.post(
        url + 'message/send/v1',
        json={
            "token": pytest.user1['token'],
            "channel_id": 2,
            "message": "TestMessage3"
        }
    )
    requests.post(
        url + 'message/send/v1',
        json={
            "token": pytest.user2['token'],
            "channel_id": 2,
            "message": "TestMessage4"
        }
    )

    requests.post(
        url + 'message/send/v1',
        json={
            "token": pytest.user1['token'],
            "channel_id": 3,
            "message": "TestMessage5"
        }
    )
    requests.post(
        url + 'message/send/v1',
        json={
            "token": pytest.user2['token'],
            "channel_id": 3,
            "message": "TestMessage6"
        }
    )

    requests.post(
        url + 'message/send/v1',
        json={
            "token": pytest.user1['token'],
            "channel_id": 4,
            "message": "TestMessage7"
        }
    )
    requests.post(
        url + 'message/send/v1',
        json={
            "token": pytest.user2['token'],
            "channel_id": 4,
            "message": "TestMessage8"
        }
    )

    # TODO:
    # Add user 1 and 2 into 2 DMs
    dm1 = requests.post(
        url + 'dm/create/v1',
        json={
            "token": pytest.user1['token'],
            "u_ids": [pytest.user2['auth_user_id']]
        }
    ).json()

    dm2 = requests.post(
        url + 'dm/create/v1',
        json={
            "token": pytest.user2['token'],
            "u_ids": [pytest.user1['auth_user_id']]
        }
    ).json()

    # For coverage
    dm2 = requests.post(
        url + 'dm/create/v1',
        json={
            "token": pytest.user1['token'],
            "u_ids": []
        }
    ).json()

    # Send 3 messages in each DM
    # User 1 send message to DM1
    requests.post(
        url + 'message/senddm/v1',
        json={
            "token": pytest.user1['token'],
            "dm_id": dm1['dm_id'],
            "message": "TestMessage1InDM"
        }
    )

    requests.post(
        url + 'message/senddm/v1',
        json={
            "token": pytest.user1['token'],
            "dm_id": dm1['dm_id'],
            "message": "TestMessage2InDM"
        }
    )

    requests.post(
        url + 'message/senddm/v1',
        json={
            "token": pytest.user1['token'],
            "dm_id": dm1['dm_id'],
            "message": "TestMessage3InDM"
        }
    )

    # User 2 send message to DM1
    requests.post(
        url + 'message/senddm/v1',
        json={
            "token": pytest.user2['token'],
            "dm_id": dm1['dm_id'],
            "message": "TestMessage4InDM"
        }
    )

    requests.post(
        url + 'message/senddm/v1',
        json={
            "token": pytest.user2['token'],
            "dm_id": dm1['dm_id'],
            "message": "TestMessage5InDM"
        }
    )

    requests.post(
        url + 'message/senddm/v1',
        json={
            "token": pytest.user2['token'],
            "dm_id": dm1['dm_id'],
            "message": "TestMessage6InDM"
        }
    )

    # User 1 send message to DM2
    requests.post(
        url + 'message/senddm/v1',
        json={
            "token": pytest.user1['token'],
            "dm_id": dm2['dm_id'],
            "message": "TestMessage1InDM"
        }
    )

    requests.post(
        url + 'message/senddm/v1',
        json={
            "token": pytest.user1['token'],
            "dm_id": dm2['dm_id'],
            "message": "TestMessage2InDM"
        }
    )

    requests.post(
        url + 'message/senddm/v1',
        json={
            "token": pytest.user1['token'],
            "dm_id": dm2['dm_id'],
            "message": "TestMessage3InDM"
        }
    )

    # User 2 send message to DM2
    requests.post(
        url + 'message/senddm/v1',
        json={
            "token": pytest.user2['token'],
            "dm_id": dm2['dm_id'],
            "message": "TestMessage4InDM"
        }
    )

    requests.post(
        url + 'message/senddm/v1',
        json={
            "token": pytest.user2['token'],
            "dm_id": dm2['dm_id'],
            "message": "TestMessage5InDM"
        }
    )

    requests.post(
        url + 'message/senddm/v1',
        json={
            "token": pytest.user2['token'],
            "dm_id": dm2['dm_id'],
            "message": "TestMessage6InDM"
        }
    )

    # User 1 remove user 2
    resp = requests.delete(
        url + 'admin/user/remove/v1',
        json={
            "token": pytest.user1['token'],
            "u_id": pytest.user2['auth_user_id']
        }
    )

    assert resp.status_code == 200

    # Make sure user is removed from channels
    channel1_details = requests.get(
        url + 'channel/details/v2',
        params={
            "token": pytest.user1['token'],
            "channel_id": 1
        }
    ).json()

    for user in channel1_details['owner_members']:
        assert user['u_id'] != pytest.user2['auth_user_id']
    for user in channel1_details['all_members']:
        assert user['u_id'] != pytest.user2['auth_user_id']

    channel2_details = requests.get(
        url + 'channel/details/v2',
        params={
            "token": pytest.user1['token'],
            "channel_id": 2
        }
    ).json()

    for user in channel2_details['owner_members']:
        assert user['u_id'] != pytest.user2['auth_user_id']
    for user in channel2_details['all_members']:
        assert user['u_id'] != pytest.user2['auth_user_id']

    channel3_details = requests.get(
        url + 'channel/details/v2',
        params={
            "token": pytest.user1['token'],
            "channel_id": 3
        }
    ).json()

    for user in channel3_details['owner_members']:
        assert user['u_id'] != pytest.user2['auth_user_id']
    for user in channel3_details['all_members']:
        assert user['u_id'] != pytest.user2['auth_user_id']

    channel4_details = requests.get(
        url + 'channel/details/v2',
        params={
            "token": pytest.user1['token'],
            "channel_id": 4
        }
    ).json()

    for user in channel4_details['owner_members']:
        assert user['u_id'] != pytest.user2['auth_user_id']
    for user in channel4_details['all_members']:
        assert user['u_id'] != pytest.user2['auth_user_id']

    # the channel messages are renamed to 'Removed user'

    channel1_messages = requests.get(
        url + 'channel/messages/v2',
        params={
            "token": pytest.user1['token'],
            "channel_id": 1,
            "start": 0
        }
    ).json()['messages']

    channel2_messages = requests.get(
        url + 'channel/messages/v2',
        params={
            "token": pytest.user1['token'],
            "channel_id": 1,
            "start": 0
        }
    ).json()['messages']

    channel3_messages = requests.get(
        url + 'channel/messages/v2',
        params={
            "token": pytest.user1['token'],
            "channel_id": 1,
            "start": 0
        }
    ).json()['messages']

    channel4_messages = requests.get(
        url + 'channel/messages/v2',
        params={
            "token": pytest.user1['token'],
            "channel_id": 1,
            "start": 0
        }
    ).json()['messages']

    channel_messages = channel1_messages + channel2_messages + channel3_messages + channel4_messages

    for message in channel_messages:
        if message['u_id'] == pytest.user2['auth_user_id']:
            assert message['message'] == 'Removed user'

    # TODO: Make sure user is removed from DMs and the messages are renamed to 'Removed user'
    dm1_details = requests.get(
        url + 'dm/details/v1',
        params={
            "token": pytest.user1['token'],
            "dm_id": 1
        }
    ).json()

    for user in dm1_details['members']:
        assert user['u_id'] != pytest.user2['auth_user_id']

    dm2_details = requests.get(
        url + 'dm/details/v1',
        params={
            "token": pytest.user1['token'],
            "dm_id": 2
        }
    ).json()

    for user in dm2_details['members']:
        assert user['u_id'] != pytest.user2['auth_user_id']

    # the dm messages are renamed to 'Removed user'
    dm1_messages = requests.get(
        url + 'dm/messages/v1',
        params={
            "token": pytest.user1['token'],
            "dm_id": 1,
            "start": 0
        }
    ).json()['messages']

    dm2_messages = requests.get(
        url + 'dm/messages/v1',
        params={
            "token": pytest.user1['token'],
            "dm_id": 2,
            "start": 0
        }
    ).json()['messages']

    dm_messages = dm1_messages + dm2_messages

    for message in dm_messages:
        if message['u_id'] == pytest.user2['auth_user_id']:
            assert message['message'] == 'Removed user'

    # Make sure user does not appear in users/all
    resp = requests.get(
        url + "users/all/v1",
        params={
            "token": pytest.user1['token']
        }
    )

    users_list = resp.json()['users']

    for user in users_list:        
        assert user['u_id'] != pytest.user2['auth_user_id']
        assert user['email'] != USER2_PAYLOAD['email']
        assert user['handle_str'] != USER2_PAYLOAD['handle_str']

    # Make sure profile is retrivable
    resp = requests.get(
        url + 'user/profile/v1',
        params={
            'token': pytest.user1['token'],
            'u_id': pytest.user2['auth_user_id']
        }
    )

    assert resp.status_code == 200

    # Make sure name_first is 'Removed' and name_last is 'user'
    user2_profile = resp.json()['user']

    assert user2_profile['name_first'] == 'Removed'
    assert user2_profile['name_last'] == 'user'

    # Make sure user cant login and all tokens are revoked
    login_user_resp = requests.post(
        url + '/auth/login/v2',
        json={
            "email": USER2_PAYLOAD['email'],
            "password": USER2_PAYLOAD['password']
        }
    )

    assert login_user_resp.status_code == 400
    
    # Whitebox test needed to make sure user sessions list is empty
    store = data_store.get()

    for user in store['users']:
        if user['user_id'] == pytest.user2['auth_user_id']:
            assert len(user['sessions']) == 0
            break

    # Check if email is reusable
    # Register new user with removed user email
    resp = requests.post(
        url + 'auth/register/v2',
        json={
            "email": USER2_PAYLOAD['email'],
            "password": "password123",
            "name_first": "Tim",
            "name_last": "Cook"
        }
    )

    assert resp.status_code == 200

    # Change the above user email to something else, we want the removed user email for the below test
    resp = requests.put(
        url + 'user/profile/setemail/v1',
        json={
            "token": resp.json()['token'],
            "email": 'emailwhichisnotinuse@email.com'
        }
    )

    # Change existing user email to removed user email
    resp = requests.put(
        url + 'user/profile/setemail/v1',
        json={
            "token": pytest.user1['token'],
            "email": USER2_PAYLOAD['email']
        }
    )

    assert resp.status_code == 200

    # Check if handle is reusable
    resp = requests.post(
        url + 'auth/register/v2',
        json={
            "email": "adadaafafffaaf@email.com",
            "password": "password123",
            "name_first": USER2_PAYLOAD['name_first'],
            "name_last": USER2_PAYLOAD['name_last']
        }
    )
     
    # Check whether the handle is used
    user_profile = requests.get(
        url + 'user/profile/v1',
        params={
            'token': resp.json()['token'],
            'u_id': resp.json()['auth_user_id']
        }
    ).json()['user']

    assert user_profile['handle_str'] == USER2_PAYLOAD['handle_str']

    # Change the above user handle to something else, we want the removed user handle for the below test
    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": resp.json()['token'],
            "handle_str": "alalalalalalalla"
        }
    )

    resp = requests.put(
        url + 'user/profile/sethandle/v1',
        json={
            "token": pytest.user1['token'],
            "handle_str": USER2_PAYLOAD['handle_str']
        }
    )
    assert resp.status_code == 200

    user_profile = requests.get(
        url + 'user/profile/v1',
        params={
            'token': pytest.user1['token'],
            'u_id': pytest.user1['auth_user_id']
        }
    ).json()['user']

    assert user_profile['handle_str'] == USER2_PAYLOAD['handle_str']
