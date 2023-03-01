import pytest
from src.channel import check_if_member, check_if_owner
from src.error import InputError, AccessError
from src.data_store import data_store
from tests.helpers import clear
import requests
from src import config

# Channel_invite_v1 tests
@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')
    user_for_coverage = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cover', 'name_last': 'Age'})
    requests.post(config.url + 'channels/create/v2', json={'token': user_for_coverage.json()['token'], 'name': 'Coverage channel', 'is_public': True})

def test_valid_invite(clear_and_register):
    # Create channel, auth and users.
    valid_auth = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'Jack', 'name_last': 'Walt'})
    valid_channel = requests.post(config.url + 'channels/create/v2', json={'token': valid_auth.json()['token'], 'name': 'TestChannel', 'is_public': True})
    valid_user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    # Use function.
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': valid_auth.json()['token'], 'channel_id': valid_channel.json()['channel_id'], 'u_id': valid_user.json()['auth_user_id']})
    print(resp.json())
    assert resp.status_code == 200

def test_invalid_channel_id(clear_and_register):
    valid_auth = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'Jack', 'name_last': 'Walt'})
    valid_user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    invalid_channel_id = 9999
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': valid_auth.json()['token'], 'channel_id': invalid_channel_id, 'u_id': valid_user.json()['auth_user_id']})
    assert resp.status_code == 400

def test_invalid_u_id(clear_and_register):
    valid_auth = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'Jack', 'name_last': 'Walt'})
    valid_channel = requests.post(config.url + 'channels/create/v2', json={'token': valid_auth.json()['token'], 'name': 'TestChannel', 'is_public': True})
    invalid_u_id = 9999
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': valid_auth.json()['token'], 'channel_id': valid_channel.json()['channel_id'], 'u_id': invalid_u_id})
    assert resp.status_code == 400

def test_invalid_auth_user_id(clear_and_register):
    channel_creator = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'Jack', 'name_last': 'Walt'})
    valid_channel = requests.post(config.url + 'channels/create/v2', json={'token': channel_creator.json()['token'], 'name': 'TestChannel', 'is_public': True})
    valid_user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    invalid_auth_id = 9999
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': invalid_auth_id, 'channel_id': valid_channel.json()['channel_id'], 'u_id': valid_user.json()['auth_user_id']})
    assert resp.status_code == 403

def test_member_already_in_channel(clear_and_register):
    valid_auth = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'Jack', 'name_last': 'Walt'})
    valid_channel = requests.post(config.url + 'channels/create/v2', json={'token': valid_auth.json()['token'], 'name': 'TestChannel', 'is_public': True})
    valid_user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    requests.post(config.url + 'channel/invite/v2', json={'token': valid_auth.json()['token'], 'channel_id': valid_channel.json()['channel_id'], 'u_id': valid_user.json()['auth_user_id']})
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': valid_auth.json()['token'], 'channel_id': valid_channel.json()['channel_id'], 'u_id': valid_user.json()['auth_user_id']})
    assert resp.status_code == 400

def test_invite_by_non_channel_member(clear_and_register):
    channel_creator = requests.post(config.url + 'auth/register/v2', json={'email': 'crazy8@gmail.com', 'password': '1234567', 'name_first': 'Jack', 'name_last': 'Walt'})
    valid_channel = requests.post(config.url + 'channels/create/v2', json={'token': channel_creator.json()['token'], 'name': 'TestChannel', 'is_public': True})
    non_channel_member = requests.post(config.url + 'auth/register/v2', json={'email': '1amazon@gmail.com', 'password': '1234567', 'name_first': 'Elon', 'name_last': 'Tusk'})
    valid_user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': non_channel_member.json()['token'], 'channel_id': valid_channel.json()['channel_id'], 'u_id': valid_user.json()['auth_user_id']})
    assert resp.status_code == 403

def test_if_member(clear_and_register):
    assert check_if_member(999,999) == False
    clear()
    assert check_if_member(999,999) == False
def test_if_owner(clear_and_register):
    assert check_if_owner(999,999) == False
    clear()
    assert check_if_owner(999,999) == False

# Tests that need to be discussed. These only test incorrect types for each input which had all already passed previously.

# def test_channel_invite_v1_input_type(clear_and_register):
#     # resp = requests.post(config.url + 'channel/invite/v2', json={'token': 'hello', 'channel_id': '12345', 'u_id': 'helloagain'})
#     # assert resp.status_code == 400
#     with pytest.raises(InputError):
#         # Test each parameter that requires integers with strings
#         channel_invite_v1('hello', '12345', 'helloagain')

# def test_channel_invite_v1_output_type(clear_and_register):
#     # Test and see if the response variables have the appropriate types
#     valid_auth_id = auth_register_v1('crazy8@gmail.com', '1234567', 'Jack', 'Walt')['auth_user_id']
#     valid_channel_id = channels_create_v1(valid_auth_id, 'TestChannel', True)['channel_id']
#     valid_user_id = auth_register_v1('amazon@gmail.com', '1234567', 'Jeff', 'Bezos')['auth_user_id']
#     output = channel_invite_v1(valid_auth_id, valid_channel_id, valid_user_id)

    # Check if its an dictionary
    # assert isinstance(output, dict)

    # # Check if the dictionary is empty
    # assert not bool(output)



# auth_register_v1('crazy8@gmail.com', '1234567', 'Jack', 'Walt')['auth_user_id']
# valid_channel_id = channels_create_v1(valid_auth_id, 'TestChannel', True)['channel_id']
# valid_user_id = auth_register_v1('amazon@gmail.com', '1234567', 'Jeff', 'Bezos')['auth_user_id']
# channel_invite_v1(valid_auth_id, valid_channel_id, valid_user_id)