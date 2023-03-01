import pytest
from src.channel import channel_invite_v1, channel_details_v1, channel_messages_v1, channel_join_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1

#Channels_create_test_v1 tests
@pytest.fixture
def clear_and_register_user():
    clear_v1()
    # Create user
    auth_user_id = auth_register_v1("user@email.com", "topsecretcode","Bob", "Bobson")['auth_user_id']

    return  auth_user_id

def test_no_name(clear_and_register_user):
    with pytest.raises(InputError):
        channels_create_v1(clear_and_register_user, "", True)
        
def test_greater_20_characters(clear_and_register_user):
    with pytest.raises(InputError):
        channels_create_v1(clear_and_register_user, "Thisisover20characters", True)

def test_correct_channel_creation(clear_and_register_user):
    channel_create_output = channels_create_v1(clear_and_register_user, "validname", True)
    assert('channel_id' in channel_create_output.keys())

def test_invalid_auth_user_id(clear_and_register_user):
    with pytest.raises(AccessError):
        channels_create_v1(1000, "channel1", True)
    
def test_channels_create_v1_output_type(clear_and_register_user):
    # Test and see if the response variables have the appropriate types
    output = channels_create_v1(clear_and_register_user, "validname", True)
    # channel_id is int
    assert isinstance(output['channel_id'], int)