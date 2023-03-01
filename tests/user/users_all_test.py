import requests

from src.config import url
from tests.helpers import clear

TEST_PASSWORD = 'bestpasswordever123'


def test_users_all_v1_successful():
    clear()
    register_users = [
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

    register_users_resp_list = []

    for user in register_users:
        resp = requests.post(
            url + "/auth/register/v2",
            json={
                "email": user['email'],
                "password": TEST_PASSWORD,
                "name_first": user['name_first'],
                "name_last": user['name_last']
            }
        )

        register_users_resp_list.append(resp)
        
    resp = requests.get(
        url + "users/all/v1",
        params={
            "token": register_users_resp_list[0].json()['token']
        }
    )

    assert resp.status_code == 200
    users_list = resp.json()['users']

    assert len(register_users) == len(users_list) and all(x in users_list for x in register_users) == True

    # Make sure sensitive information is not shown
    for user in users_list:
        assert 'password' not in set(user.keys())
