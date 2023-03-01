import pytest
import requests

from src import config

from src.error import *

@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')
    pytest.user1 = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    pytest.user2 = requests.post(config.url + 'auth/register/v2', json={'email': 'testadmin@test.com', 'password': 'password', 'name_first': 'Nicholas', 'name_last': 'Decsease'})
    pytest.channel1 = requests.post(config.url + 'channels/create/v2', json={'token': pytest.user1.json()['token'], 'name': 'testchannel', 'is_public': True})
    return

def test_normal_case(clear_and_register):
    resp =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Test"})
    message = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'start': 0})
    assert message.json()['messages'][0]['message_id'] == resp.json()['message_id']

def test_channel_id_invalid(clear_and_register):
    resp = requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': 0, 'message': "Test"})
    assert resp.status_code == InputError.code

def test_message_less_1_char(clear_and_register):
    resp = requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': ""})
    assert resp.status_code == InputError.code

def test_message_greater_1000_char(clear_and_register):
    resp = requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Na"})
    assert resp.status_code == InputError.code

def test_user_not_member(clear_and_register):
    resp = requests.post(config.url + 'message/send/v1', json={'token': pytest.user2.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "hi"})
    assert resp.status_code == AccessError.code