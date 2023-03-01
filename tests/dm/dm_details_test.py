import pytest
from src.error import *
import requests
import json
from src import config
from tests.helpers import clear

@pytest.fixture
def clear_and_register():
    clear()
    pytest.user1 = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'}).json()
    pytest.user2 = requests.post(config.url + 'auth/register/v2', json={'email': 'elon@gmail.com', 'password': '1234567', 'name_first': 'Elon', 'name_last': 'Musk'}).json()
    pytest.user3 = requests.post(config.url + 'auth/register/v2', json={'email': 'steve@apple.com', 'password': '1234567', 'name_first': 'Steve', 'name_last': 'Jobs'}).json()

    # DM1 - Owner 1, Users 2, 3
    pytest.dm1 = requests.post(config.url + 'dm/create/v1', json={'token': pytest.user1['token'], 'u_ids': [pytest.user2['auth_user_id'], pytest.user3['auth_user_id']]}).json()
    # DM2 - Owner 2, Users 3
    pytest.dm2 = requests.post(config.url + 'dm/create/v1', json={'token': pytest.user2['token'], 'u_ids': [pytest.user3['auth_user_id']]}).json()

# { name, is_public, owner_members, all_members }

def test_dm_details_v1_successful(clear_and_register):
    user1_profile = requests.get(config.url + 'user/profile/v1', params={'token': pytest.user1['token'], 'u_id': pytest.user1['auth_user_id']}).json()['user']
    user2_profile = requests.get(config.url + 'user/profile/v1', params={'token': pytest.user2['token'], 'u_id': pytest.user2['auth_user_id']}).json()['user']
    user3_profile = requests.get(config.url + 'user/profile/v1', params={'token': pytest.user3['token'], 'u_id': pytest.user3['auth_user_id']}).json()['user']

    dm1_name = ', '.join(sorted([user1_profile['handle_str'], user2_profile['handle_str'], user3_profile['handle_str']]))

    resp = requests.get(config.url + 'dm/details/v1', params={'token': pytest.user1['token'], 'dm_id': pytest.dm1['dm_id']})

    assert json.loads(resp.text) == {
        'name': dm1_name,
        'members': [
            {
                'u_id': user1_profile['u_id'],
                'email': user1_profile['email'],
                'name_first': user1_profile['name_first'],
                'name_last': user1_profile['name_last'],
                'handle_str': user1_profile['handle_str'],
                'profile_img_url': user1_profile['profile_img_url'],
            },
            {
                'u_id': user2_profile['u_id'],
                'email': user2_profile['email'],
                'name_first': user2_profile['name_first'],
                'name_last': user2_profile['name_last'],
                'handle_str': user2_profile['handle_str'],
                'profile_img_url': user2_profile['profile_img_url'],
            },
            {
                'u_id': user3_profile['u_id'],
                'email': user3_profile['email'],
                'name_first': user3_profile['name_first'],
                'name_last': user3_profile['name_last'],
                'handle_str': user3_profile['handle_str'],
                'profile_img_url': user3_profile['profile_img_url'],
            },
        ]
    }


    dm2_name = ', '.join(sorted([user2_profile['handle_str'], user3_profile['handle_str']]))

    resp = requests.get(config.url + 'dm/details/v1', params={'token': pytest.user3['token'], 'dm_id': pytest.dm2['dm_id']})

    assert json.loads(resp.text) == {
        'name': dm2_name,
        'members': [
            {
                'u_id': user2_profile['u_id'],
                'email': user2_profile['email'],
                'name_first': user2_profile['name_first'],
                'name_last': user2_profile['name_last'],
                'handle_str': user2_profile['handle_str'],
                'profile_img_url': user2_profile['profile_img_url'],
            },
            {
                'u_id': user3_profile['u_id'],
                'email': user3_profile['email'],
                'name_first': user3_profile['name_first'],
                'name_last': user3_profile['name_last'],
                'handle_str': user3_profile['handle_str'],
                'profile_img_url': user3_profile['profile_img_url'],
            },
        ]
    }


def test_invalid_dm_id(clear_and_register):
    invalid_dm_id = 9999
    resp = requests.get(config.url + 'dm/details/v1', params={'token': pytest.user1['token'], 'dm_id': invalid_dm_id})
    assert resp.status_code == 400


def test_unauthorised_access(clear_and_register):
    resp = requests.get(config.url + 'dm/details/v1', params={'token': pytest.user1['token'], 'dm_id': pytest.dm2['dm_id']})
    assert resp.status_code == 403

