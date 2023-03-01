import requests
import pylint

from src.config import url
from tests.helpers import clear

TEST_PASSWORD = 'bestpasswordever123'


def test_user_profile_v1_u_id_does_not_refer_to_a_valid_user():
    clear()
    resp = requests.post(
        url + "/auth/register/v2",
        json={   
            "email": "steve@steve.com",
            "password": TEST_PASSWORD,
            "name_first": "Steve",
            "name_last": "Jobs"
        }
    )

    token = resp.json()['token']

    user_profile_resp = requests.get(
        url + 'user/profile/v1',
        params={
            'u_id': 0,
            'token': token
        }
    )

    assert user_profile_resp.status_code == 400

    user_profile_resp = requests.get(
        url + 'user/profile/v1',
        params={
            'u_id': 2,
            'token': token
        }
    )

    assert user_profile_resp.status_code == 400


def test_user_profile_v1_successful():
    clear()
    users = [
        {   
            "u_id": 1,
            "email": "steve@steve.com",
            "name_first": "Steve",
            "name_last": "Jobs",
            "handle_str": "stevejobs",
            'profile_img_url': f'{url}user/profile/image/default_profile_photo.jpg'
        },
        {   
            "u_id": 2,
            "email": "fakeemail1@email.com",
            "name_first": "John",
            "name_last": "Bob",
            "handle_str": "johnbob",
            'profile_img_url': f'{url}user/profile/image/default_profile_photo.jpg'
        },
        {
            "u_id": 3,
            "email": "fakeemail2@email.com",
            "name_first": "John",
            "name_last": "Johnson",
            "handle_str": "johnjohnson",
            'profile_img_url': f'{url}user/profile/image/default_profile_photo.jpg'
        },
        {
            "u_id": 4,
            "email": "fakeemail3@email.com",
            "name_first": "Jane",
            "name_last": "Janeson",
            "handle_str": "janejaneson",
            'profile_img_url': f'{url}user/profile/image/default_profile_photo.jpg'
        },
        {
            "u_id": 5,
            "email": "fakeemail4@email.com",
            "name_first": "Bob",
            "name_last": "Cook",
            "handle_str": "bobcook",
            'profile_img_url': f'{url}user/profile/image/default_profile_photo.jpg'
        }
    ]

    for user in users:
        resp = requests.post(
            url + "/auth/register/v2",
            json={
                "email": user['email'],
                "password": TEST_PASSWORD,
                "name_first": user['name_first'],
                "name_last": user['name_last']
            }
        )

        # users_resp_list.append(resp)
        user['token'] = resp.json()['token']
        user['auth_user_id'] = resp.json()['auth_user_id']
    
    # Own user check own user profile
    for user in users:
        token = user['token']
        auth_user_id = user['auth_user_id']

        user_profile_resp = requests.get(
            url + 'user/profile/v1',
            params={
                'token': token,
                'u_id': auth_user_id
            }
        )

        assert user_profile_resp.status_code == 200
        user_profile = user_profile_resp.json()['user']

        user.pop('token')
        user.pop('auth_user_id')

        assert user == user_profile

        user['token'] = token
        user['auth_user_id'] = auth_user_id

    # User checking each other's profile
    for user in users:
        for other_user in users:
            token = other_user['token']
            auth_user_id = other_user['auth_user_id']

            user_profile_resp = requests.get(
                url + 'user/profile/v1',
                params={
                    'token': user['token'],
                    'u_id': auth_user_id
                }
            )

            assert user_profile_resp.status_code == 200
            user_profile = user_profile_resp.json()['user']

            other_user.pop('token')
            other_user.pop('auth_user_id')

            assert other_user == user_profile

            other_user['token'] = token
            other_user['auth_user_id'] = auth_user_id

