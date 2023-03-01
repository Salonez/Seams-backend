import pytest
import requests

from src.config import url
from src.auth import auth_register_v1
from tests.helpers import clear

TEST_EMAIL = 'steve@steve.com'
TEST_PASSWORD = 'bestpasswordever123'
TEST_NAME_FIRST = 'Steve'
TEST_NAME_LAST = 'Jobs'


# @pytest.fixture
# def clear_and_register():
#     clear()
#     return requests.post(
#         url + '/auth/register/v2',
#         json={
#             "email": TEST_EMAIL,
#             "password": TEST_PASSWORD,
#             "name_first": TEST_NAME_FIRST,
#             "name_last": TEST_NAME_LAST
#         }
#     ).json()
#     return auth_register_v1(TEST_EMAIL, TEST_PASSWORD, TEST_NAME_FIRST, TEST_NAME_LAST)


# Register
def test_auth_register_v2_invalid_email():
    clear()
    # with pytest.raises(InputError):
    #     auth_register_v1('steve!steve', TEST_PASSWORD, TEST_NAME_FIRST, TEST_NAME_LAST)
    resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": "steve!steve",
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    )
    assert resp.status_code == 400


def test_auth_register_v2_email_already_in_use():
    clear()
    # with pytest.raises(InputError):
    #     auth_register_v1(TEST_EMAIL, TEST_PASSWORD, TEST_NAME_FIRST, TEST_NAME_LAST)
    first_user_resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    )
    assert first_user_resp.status_code == 200
    
    second_user_resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    )
    assert second_user_resp.status_code == 400


# Test if password is lesser than 6 charaters
def test_auth_register_v2_password_length():
    clear()
    # with pytest.raises(InputError):
    #     auth_register_v1(TEST_EMAIL, '123', TEST_NAME_FIRST, TEST_NAME_LAST)
    resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": "123",
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    )
    assert resp.status_code == 400


def test_auth_register_v2_name_first_length():
    clear()
    # with pytest.raises(InputError):
    #     # First, test and see whether it accepts an empty string.
    #     auth_register_v1(TEST_EMAIL, TEST_PASSWORD, '', TEST_NAME_LAST)
    #     # Next, test and see whether it accepts a name longer than 50 characters.
    #     clear_v1()
    #     auth_register_v1(
    #         TEST_EMAIL,
    #         TEST_PASSWORD,
    #         'verylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongname',
    #         TEST_NAME_LAST
    #     )
    resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": '',
            "name_last": TEST_NAME_LAST
        }
    )
    assert resp.status_code == 400
    clear()
    resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": 'verylongname'*100,
            "name_last": TEST_NAME_LAST
        }
    )
    assert resp.status_code == 400


def test_auth_register_v2_name_last_length():
    clear()
    # with pytest.raises(InputError):
    # # First, test and see whether it accepts an empty string.
    #     auth_register_v1(TEST_EMAIL, TEST_PASSWORD, TEST_NAME_FIRST, '')
    #     # Next, test and see whether it accepts a name longer than 50 characters.
    #     clear_v1()
    #     auth_register_v1(
    #         TEST_EMAIL,
    #         TEST_PASSWORD,
    #         TEST_NAME_FIRST,
    #         'verylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongname'
    #     )
    resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": ''
        }
    )
    assert resp.status_code == 400
    clear()
    resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": 'verylongname'*100
        }
    )
    assert resp.status_code == 400


def test_auth_register_v2_successful_registration():
    # clear_v1()
    # assert auth_register_v1(
    #     TEST_EMAIL,
    #     TEST_PASSWORD,
    #     TEST_NAME_FIRST,
    #     TEST_NAME_LAST
    # ) == {'auth_user_id': 1}
    clear()
    register_user_resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    )
    assert register_user_resp.status_code == 200
    assert register_user_resp.json()['auth_user_id'] == 1
    
    # Test token
    channels_create_resp = requests.post(
        url + '/channels/create/v2',
        json={
            "token": register_user_resp.json()['token'],
            "name": "ATestChannelName",
            "is_public": True
        }
    )

    assert channels_create_resp.status_code == 200


def test_auth_register_v2_successful_registration_with_multiple_same_names():
    clear()
    # first_user_id = auth_register_v1(
    #     TEST_EMAIL,
    #     TEST_PASSWORD,
    #     'abc',
    #     'def0'
    # )['auth_user_id']
    first_user_resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": "abc",
            "name_last": "def0"
        }
    )

    assert first_user_resp.status_code == 200
    first_user_handle_str = 'abcdef0'
    
    # second_user_id = auth_register_v1(
    #     'abc@aaa.com',
    #     TEST_PASSWORD,
    #     'abc',
    #     'def'
    # )['auth_user_id']

    second_user_resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": "abc@aaa.com",
            "password": TEST_PASSWORD,
            "name_first": "abc",
            "name_last": "def"
        }
    )

    assert second_user_resp.status_code == 200
    second_user_handle_str = 'abcdef'

    # third_user_id = auth_register_v1(
    #     'abcde@aaa.com',
    #     TEST_PASSWORD,
    #     'abc',
    #     'def'
    # )['auth_user_id']

    third_user_resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": "abcde@aaa.com",
            "password": TEST_PASSWORD,
            "name_first": "abc",
            "name_last": "def"
        }
    )

    assert third_user_resp.status_code == 200 
    third_user_handle_str = 'abcdef1'

    first_user_id = first_user_resp.json()['auth_user_id']
    first_user_token = first_user_resp.json()['token']

    second_user_id = second_user_resp.json()['auth_user_id']
    second_user_token = second_user_resp.json()['token']

    third_user_id = third_user_resp.json()['auth_user_id']
    third_user_token = third_user_resp.json()['token']

    channel_create_resp = requests.post(
        url + '/channels/create/v2',
        json={
            "token": first_user_token,
            "name": "FirstChannel",
            "is_public": True
        }
    )

    assert channel_create_resp.status_code == 200

    second_user_join_channel_resp = requests.post(
        url + '/channel/join/v2',
        json={
            "token": second_user_token,
            "channel_id": channel_create_resp.json()['channel_id']
        }
    )

    assert second_user_join_channel_resp.status_code == 200

    third_user_join_channel_resp = requests.post(
        url + '/channel/join/v2',
        json={
            "token": third_user_token,
            "channel_id": channel_create_resp.json()['channel_id']
        }
    )

    assert third_user_join_channel_resp.status_code == 200

    channel_details_resp = requests.get(
        url + '/channel/details/v2',
        params={
            "token": first_user_token,
            "channel_id": channel_create_resp.json()['channel_id']
        }
    )

    assert channel_details_resp.status_code == 200

    # channel_create_response = channels_create_v1(first_user_id, 'FirstChannel', True)
    # channel_join_v1(second_user_id, channel_create_response['channel_id'])
    # channel_join_v1(third_user_id, channel_create_response['channel_id'])

    # channel_details = channel_details_v1(first_user_id, channel_create_response['channel_id'])

    for channel_member in channel_details_resp.json()['all_members']:
        if channel_member['u_id'] == first_user_id:
            assert channel_member['handle_str'] == first_user_handle_str

        elif channel_member['u_id'] == second_user_id:
            assert channel_member['handle_str'] == second_user_handle_str
        
        elif channel_member['u_id'] == third_user_id:
            assert channel_member['handle_str'] == third_user_handle_str


def test_auth_register_v2_only_first_user_has_global_permissions_upon_creation():
    clear()
    # Create first user
    first_user_resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    )
    assert first_user_resp.status_code == 200

    # Create second user
    second_user_resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": 'anotheremail@email.com',
            "password": TEST_PASSWORD,
            "name_first": 'TEST_NAME_FIRST',
            "name_last": TEST_NAME_LAST
        }
    )
    assert second_user_resp.status_code == 200

    # TODO: Wait for admin functions to be ready
    # # Second user (who should not have global permissions), will attempt to remove first user
    # user_remove_resp = requests.post(
    #     url + '/admin/user/remove/v1',
    #     json={
    #         "token": second_user_resp.json()['token'],
    #         "u_id": first_user_resp.json()['auth_user_id']
    #     }
    # )

    # assert user_remove_resp.status_code == 403


def test_auth_register_v2_first_user_has_global_permissions():
    clear()
    # Create first user
    first_user_resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    )
    assert first_user_resp.status_code == 200

    # Create second user
    second_user_resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": 'anotheremail@email.com',
            "password": TEST_PASSWORD,
            "name_first": 'TEST_NAME_FIRST',
            "name_last": TEST_NAME_LAST
        }
    )
    assert second_user_resp.status_code == 200

    # TODO: Wait for admin functions to be ready
    # First user (who should have global permissions), will remove second user
    # user_remove_resp = requests.post(
    #     url + '/admin/user/remove/v1',
    #     json={
    #         "token": first_user_resp.json()['token'],
    #         "u_id": second_user_resp.json()['auth_user_id']
    #     }
    # )

    # assert user_remove_resp.status_code == 200


# def test_auth_register_v1_input_type():
#     with pytest.raises(InputError):
#         clear_v1()
#         # Test each parameter that requires strings with integers
#         auth_register_v1(12345, TEST_PASSWORD, TEST_NAME_FIRST, TEST_NAME_LAST)


def test_auth_register_v2_output_type():
    clear()
    # Test and see if the response variables have the appropriate types
    resp = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    )
    assert resp.status_code == 200

    # auth_user_id is int
    # token is str
    assert isinstance(resp.json()['auth_user_id'], int) is True
    assert isinstance(resp.json()['token'], str) is True
