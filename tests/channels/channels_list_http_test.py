import requests
import pytest

from src.channels import channels_list_v1
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1
from src.error import InputError, AccessError
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.config import url
from tests.helpers import clear

@pytest.fixture
def clear_and_register():
    clear()
    pytest.user1 = requests.post(url + 'auth/register/v2', 
        json={  'email': 'person1@hello.com', 
                'password': 'happybirthday', 
                'name_first': 'John', 
                'name_last': 'Doe'})
    pytest.user2 = requests.post(url + 'auth/register/v2', 
        json={  'email': 'person2@hello.com', 
                'password': 'happybirthday', 
                'name_first': 'Fred', 
                'name_last': 'Long'})
    pytest.channel1 = requests.post(url + 'channels/create/v2', 
        json={  'token': pytest.user1.json()['token'], 
                'name': 'channel1', 
                'is_public': True})   
    pytest.channel2 = requests.post(url + 'channels/create/v2', 
        json={  'token': pytest.user2.json()['token'], 
                'name': 'channel2', 
                'is_public': True})  
    pytest.joined2 = requests.post(url + 'channel/join/v2',
        json={  'token': pytest.user1.json()['token'], 
                'channel_id': pytest.channel2.json()['channel_id']})  
    return

def test_no_id_http():
    response = requests.get(url + '/channels/list/v2', json={'token': 'hello'})
    assert response.status_code == 403


def test_user_in_one_channel_http(clear_and_register):
    response = requests.get(url + "channels/list/v2", params={'token': pytest.user2.json()['token']})
    response_data = response.json()
    assert (response.status_code == 200)
    assert (len(response_data) == 1)
    assert ('channel_id' in response_data['channels'][0].keys())
    assert ('name' in response_data['channels'][0].keys())    


def test_user_in_two_channels_http(clear_and_register):
    response = requests.get(url + "/channels/list/v2", params={'token': pytest.user1.json()['token']})
    response_data = response.json()
    assert (response.status_code == 200)
    assert (len(response_data['channels']) == 2)
    assert ('channel_id' in response_data['channels'][0].keys())
    assert ('name' in response_data['channels'][0].keys())
    assert ('channel_id' in response_data['channels'][1].keys())
    assert ('name' in response_data['channels'][1].keys())

def test_channels_list_v1_output_type_http(clear_and_register):
    response = requests.get(url + "channels/list/v2", params={'token': pytest.user2.json()['token']})
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data.keys() == {'channels'}

    valid_channel_dict_keys = {'channel_id', 'name'}
    # channels is a list of channels dict
    assert isinstance(response_data['channels'], list)

    # Check every member's dict key type
    for channel in response_data['channels']:
        channel_dict_keys = channel.keys()
        assert len(channel_dict_keys) == len(valid_channel_dict_keys)
        assert channel_dict_keys == valid_channel_dict_keys
        assert isinstance(channel['channel_id'], int)
        assert isinstance(channel['name'], str)



