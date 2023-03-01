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
    pytest.dm1 = requests.post(config.url + 'dm/create/v1', json={'token': pytest.user1.json()['token'], 'u_ids': [2]})
    pytest.dm2 = requests.post(config.url + 'dm/create/v1', json={'token': pytest.user2.json()['token'], 'u_ids': []})
    return

def test_normal_function(clear_and_register):
    message = requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    requests.put(config.url + 'message/edit/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'message': "LOL"})
    resp = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'start': 0})
    assert resp.json()['messages'][0]['message'] == "LOL"

def test_normal_function_second_message_edited(clear_and_register):
    message = requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "XD"})
    requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    requests.put(config.url + 'message/edit/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'message': "LOL"})
    resp = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'start': 0})
    assert resp.json()['messages'][1]['message'] == "LOL"

def test_edit_empty_message(clear_and_register):
    message = requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    requests.put(config.url + 'message/edit/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'message': ""})
    resp = requests.get(config.url + 'channel/messages/v2', params={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'start': 0})
    assert resp.json()['messages'] == []

def test_edit_greater_1000_char(clear_and_register):
    message = requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    resp = requests.put(config.url + 'message/edit/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'message': "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Na"})
    assert resp.status_code == InputError.code

def test_invalid_id_user_not_joined(clear_and_register):
    message = requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    resp = requests.put(config.url + 'message/edit/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id'], 'message': "LOL"})
    assert resp.status_code == InputError.code

def test_invalid_id_0(clear_and_register):
    requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    resp = requests.put(config.url + 'message/edit/v1', json={'token': pytest.user1.json()['token'], 'message_id': 0, 'message': "LOL"})
    assert resp.status_code == InputError.code

def test_wasnt_sent_by_user(clear_and_register):
    requests.post(config.url + 'channel/join/v2', json={'token': pytest.user2.json()['token'], 'channel_id': pytest.channel1.json()['channel_id']})
    message = requests.post(config.url + 'message/send/v1', json={'token': pytest.user1.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    resp = requests.put(config.url + 'message/edit/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id'], 'message': "LOL"})
    assert resp.status_code == AccessError.code

def test_wasnt_sent_by_user_but_is_owner(clear_and_register):
    requests.post(config.url + 'channel/join/v2', json={'token': pytest.user2.json()['token'], 'channel_id': pytest.channel1.json()['channel_id']})
    message = requests.post(config.url + 'message/send/v1', json={'token': pytest.user2.json()['token'], 'channel_id': pytest.channel1.json()['channel_id'], 'message': "Hi"})
    resp = requests.put(config.url + 'message/edit/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'message': "LOL"})
    assert resp.json() == {}

def test_dm_normal_function(clear_and_register):
    message = requests.post(config.url + 'message/senddm/v1', json={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'message': "Hi"})
    requests.put(config.url + 'message/edit/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'message': "LOL"})
    resp = requests.get(config.url + 'dm/messages/v1', params={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'start': 0})
    assert resp.json()['messages'][0]['message'] == "LOL"

def test_dm_no_permission_to_change(clear_and_register):
    message = requests.post(config.url + 'message/senddm/v1', json={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'message': "Hi"})
    resp = requests.put(config.url + 'message/edit/v1', json={'token': pytest.user2.json()['token'], 'message_id': message.json()['message_id'], 'message': "LOL"})
    assert resp.status_code == AccessError.code

def test_dm_bad_id(clear_and_register):
    requests.post(config.url + 'message/senddm/v1', json={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'message': "Hi"})
    resp = requests.put(config.url + 'message/edit/v1', json={'token': pytest.user2.json()['token'], 'message_id': 0, 'message': "LOL"})
    assert resp.status_code == InputError.code

def test_dm_empty_edit(clear_and_register):
    message = requests.post(config.url + 'message/senddm/v1', json={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'message': "Hi"})
    requests.put(config.url + 'message/edit/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'], 'message': ""})
    resp = requests.get(config.url + 'dm/messages/v1', params={'token': pytest.user1.json()['token'], 'dm_id': pytest.dm1.json()['dm_id'], 'start': 0})

    response_data = resp.json()
    
    assert response_data == {
        'messages': [], 
        'start': 0,
        'end': -1 
    }