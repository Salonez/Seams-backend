import pytest
from src.error import *
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.data_store import data_store
from src.other import clear_v1
import requests
import json
from src import config
from tests.helpers import clear

@pytest.fixture
def clear_and_register():
    clear()
    user_for_coverage = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cover', 'name_last': 'Age'})
    requests.post(config.url + 'channels/create/v2', json={'token': user_for_coverage.json()['token'], 'name': 'Coverage channel', 'is_public': True})

# { name, is_public, owner_members, all_members }

def test_normal_public(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'TestChannel', 'is_public': True})
    user1 = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    user2 = requests.post(config.url + 'auth/register/v2', json={'email': 'elon@gmail.com', 'password': '1234567', 'name_first': 'Elon', 'name_last': 'Musk'})
    requests.post(config.url + 'channel/join/v2', json={'token': user1.json()['token'], 'channel_id': channel.json()['channel_id']})
    requests.post(config.url + 'channel/join/v2', json={'token': user2.json()['token'], 'channel_id': channel.json()['channel_id']})
    resp = requests.get(config.url + 'channel/details/v2', params={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id']})
    assert json.loads(resp.text) == {
        'name': 'TestChannel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': creator.json()['auth_user_id'],
                'email': 'crazy8@gmail.com',
                'name_first': 'John',
                'name_last': 'Walt',
                'handle_str': 'johnwalt',
                'profile_img_url': f'{config.url}user/profile/image/default_profile_photo.jpg'
                
            },
        ],
        'all_members': [
            {
                'u_id': creator.json()['auth_user_id'],
                'email': 'crazy8@gmail.com',
                'name_first': 'John',
                'name_last': 'Walt',
                'handle_str': 'johnwalt',
                'profile_img_url': f'{config.url}user/profile/image/default_profile_photo.jpg'
            },
            {
                'u_id': user1.json()['auth_user_id'],
                'email': 'amazon@gmail.com',
                'name_first': 'Jeff',
                'name_last': 'Bezos',
                'handle_str': 'jeffbezos',   
                'profile_img_url': f'{config.url}user/profile/image/default_profile_photo.jpg'
            },
            {
                'u_id': user2.json()['auth_user_id'],
                'email': 'elon@gmail.com',
                'name_first': 'Elon',
                'name_last': 'Musk',
                'handle_str': 'elonmusk',   
                'profile_img_url': f'{config.url}user/profile/image/default_profile_photo.jpg'
            },
        ]
    }

def test_normal_private(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    private_channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'Private Channel', 'is_public': False})
    member = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    requests.post(config.url + 'channel/invite/v2', json={'token': creator.json()['token'], 'channel_id': private_channel.json()['channel_id'], 'u_id': member.json()['auth_user_id']})
    resp = requests.get(config.url + 'channel/details/v2', params={'token': creator.json()['token'], 'channel_id': private_channel.json()['channel_id']})
    assert json.loads(resp.text) == {
        'name': 'Private Channel',
        'is_public': False,
        'owner_members': [
            {
                'u_id': creator.json()['auth_user_id'],
                'email': 'crazy8@gmail.com',
                'name_first': 'John',
                'name_last': 'Walt',
                'handle_str': 'johnwalt',
                'profile_img_url': f'{config.url}user/profile/image/default_profile_photo.jpg'
            },
        ],
        'all_members': [
            {
                'u_id': creator.json()['auth_user_id'],
                'email': 'crazy8@gmail.com',
                'name_first': 'John',
                'name_last': 'Walt',
                'handle_str': 'johnwalt',
                'profile_img_url': f'{config.url}user/profile/image/default_profile_photo.jpg'
            },
            {
                'u_id': member.json()['auth_user_id'],
                'email': 'amazon@gmail.com',
                'name_first': 'Jeff',
                'name_last': 'Bezos',
                'handle_str': 'jeffbezos',  
                'profile_img_url': f'{config.url}user/profile/image/default_profile_photo.jpg'
            },
        ]
    }

def test_invalid_channel_id(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    invalid_channel_id = 9999
    resp = requests.get(config.url + 'channel/details/v2', params={'token': creator.json()['token'], 'channel_id': invalid_channel_id})
    assert resp.status_code == 400

def test_unauthorised_access(clear_and_register):
    creator = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'John', 'name_last': 'Walt'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'TestChannel', 'is_public': True})
    unauthorised_user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    resp = requests.get(config.url + 'channel/details/v2', params={'token': unauthorised_user.json()['token'], 'channel_id': channel.json()['channel_id']})
    assert resp.status_code == 403


# def test_channel_details_v1_input_type(clear_and_register):
#     valid_auth_id = auth_register_v1('crazy8@gmail.com', '1234567', 'Jack', 'Walt')['auth_user_id']
#     valid_channel_id = channels_create_v1(valid_auth_id, 'TestChannel', True)['channel_id']
#     with pytest.raises(InputError):
#         # Test each parameter that requires integers with strings
#         channel_details_v1('12345', '12345')
#         channel_details_v1('hello', 'hello')

#         # Test each parameter with None
#         channel_details_v1(None, valid_channel_id)
#         channel_details_v1(valid_auth_id, None)

# def test_channel_details_v1_output_type(clear_and_register):
#     valid_output_dict_keys = {'name', 'is_public', 'owner_members', 'all_members'}
#     valid_auth_id = auth_register_v1('crazy8@gmail.com', '1234567', 'Jack', 'Walt')['auth_user_id']
#     valid_channel_id = channels_create_v1(valid_auth_id, 'TestChannel', True)['channel_id']
#     member_id = auth_register_v1('amazon@gmail.com', '1234567', 'Jeff', 'Bezos')['auth_user_id']
#     channel_join_v1(member_id, valid_channel_id)
#     # Test and see if the response variables have the appropriate types
#     output = channel_details_v1(valid_auth_id, valid_channel_id)
#     output_dict_keys = output.keys()

#     assert len(output_dict_keys) == len(valid_output_dict_keys)
#     assert output_dict_keys == valid_output_dict_keys

#     # name is string
#     assert isinstance(output['name'], str)
#     # is_public is boolean
#     assert isinstance(output['is_public'], bool)

#     valid_user_dict_keys = {'u_id', 'email', 'name_first', 'name_last', 'handle_str'}
#     # owner_members is a list of users dict
#     assert isinstance(output['owner_members'], list)

#     # Check every member's dict key type
#     for user in output['owner_members']:
#         user_dict_keys = user.keys()
#         assert len(user_dict_keys) == len(valid_user_dict_keys)
#         assert user_dict_keys == valid_user_dict_keys
#         assert isinstance(user['u_id'], int)
#         assert isinstance(user['email'], str)
#         assert isinstance(user['name_first'], str)
#         assert isinstance(user['name_last'], str)
#         assert isinstance(user['handle_str'], str)

#     # all_members is a list of users dict
#     assert isinstance(output['all_members'], list)

#     # Check every member's dict key type
#     for user in output['owner_members']:
#         user_dict_keys = user.keys()
#         assert len(user_dict_keys) == len(valid_user_dict_keys)
#         assert user_dict_keys == valid_user_dict_keys
#         assert isinstance(user['u_id'], int)
#         assert isinstance(user['email'], str)
#         assert isinstance(user['name_first'], str)
#         assert isinstance(user['name_last'], str)
#         assert isinstance(user['handle_str'], str)
