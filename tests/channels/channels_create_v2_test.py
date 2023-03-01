import pytest
from src.channel import channel_invite_v1, channel_details_v1, channel_messages_v1, channel_join_v1
from src.error import *
from src.other import clear_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
import requests
import json
from src.config import url
from tests.helpers import clear

#Channels_create_test_v1 tests
@pytest.fixture
def clear_and_register_user():
    clear()
    # Create user
    pytest.registered_user = requests.post(url + 'auth/register/v2', json={'email': 'user@email.com', 'password': 'topsecretcode', 'name_first': 'Bob', 'name_last': 'Bobson'})

def test_no_name(clear_and_register_user):
    resp = requests.post(url + 'channels/create/v2', json={'token': pytest.registered_user.json()['token'], 'name': '', 'is_public': True})
    assert resp.status_code == 400

        
def test_greater_20_characters(clear_and_register_user):
    resp = requests.post(url + 'channels/create/v2', json={'token': pytest.registered_user.json()['token'], 'name': 'Thisisover20characters', 'is_public': True})
    assert resp.status_code == 400

def test_correct_channel_creation(clear_and_register_user):
    channel_create_output = requests.post(url + 'channels/create/v2', json={'token': pytest.registered_user.json()['token'], 'name': 'validname', 'is_public' : True})
    assert channel_create_output.status_code == 200
    assert channel_create_output.json()['channel_id'] == 1

def test_invalid_token(clear_and_register_user):
    resp = requests.post(url +  'channels/create/v2', json={'token': 'Invalidtoken', 'name': 'validname', 'is_public': True})
    assert resp.status_code == 403
    
def test_channels_create_v1_output_type(clear_and_register_user):
    # Test and see if the response variables have the appropriate types
    resp = requests.post(url + 'channels/create/v2', json={'token': pytest.registered_user.json()['token'], 'name': 'validname', 'is_public' : True})
    # channel_id is int
    assert isinstance(resp.json()['channel_id'], int)