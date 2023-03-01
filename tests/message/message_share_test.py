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
    pytest.channel2 = requests.post(config.url + 'channels/create/v2', json={'token': pytest.user2.json()['token'], 'name': 'testchannel', 'is_public': True})
    pytest.dm1 = requests.post(config.url + 'dm/create/v1', json={'token': pytest.user1.json()['token'], 'u_ids': []})
    pytest.dm2 = requests.post(config.url + 'dm/create/v1', json={'token': pytest.user2.json()['token'], 'u_ids': []})
    return

def test_both_dm_channel_id_invalid(clear_and_register):
    message =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Hi"})
    resp = requests.post(config.url + 'message/share/v1', json={'token': pytest.user1.json()['token'], 'og_message_id': message.json()['message_id'], 'message':"YO", 'channel_id': 0, 'dm_id': 0})
    assert resp.status_code == InputError.code

def test_both_dm_channel_id_negative1(clear_and_register):
    message =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Hi"})
    resp = requests.post(config.url + 'message/share/v1', json={'token': pytest.user1.json()['token'], 'og_message_id': message.json()['message_id'], 'message':"YO", 'channel_id': -1, 'dm_id': -1})
    assert resp.status_code == InputError.code

def test_invalid_message_id(clear_and_register):
    requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Hi"})
    resp = requests.post(config.url + 'message/share/v1', json={'token': pytest.user1.json()['token'], 'og_message_id': 0, 'message':"YO", 'channel_id': pytest.channel1.json()['channel_id'], 'dm_id': -1})
    assert resp.status_code == InputError.code

def test_user_not_join_channel(clear_and_register):
    message =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Hi"})
    resp = requests.post(config.url + 'message/share/v1', json={'token': pytest.user2.json()['token'], 'og_message_id': message.json()['message_id'], 'message':"YO", 'channel_id': pytest.channel2.json()['channel_id'], 'dm_id': -1})
    assert resp.status_code == InputError.code

def test_user_not_join_dm(clear_and_register):
    message =  requests.post(config.url + 'message/senddm/v1', json={'token':pytest.user1.json()['token'],'dm_id':pytest.dm1.json()['dm_id'],'message':"Hi"})
    resp = requests.post(config.url + 'message/share/v1', json={'token': pytest.user2.json()['token'], 'og_message_id': message.json()['message_id'], 'message':"YO", 'channel_id': -1, 'dm_id': pytest.dm2.json()['dm_id']})
    assert resp.status_code == InputError.code

def test_greater_than_1000_char(clear_and_register):
    message =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Hi"})
    resp = requests.post(config.url + 'message/share/v1', json={'token': pytest.user1.json()['token'], 'og_message_id': message.json()['message_id'], 'message':"Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Na", 'channel_id': pytest.channel1.json()['channel_id'], 'dm_id': -1})
    assert resp.status_code == InputError.code

def test_send_to_invlaid_channel(clear_and_register):
    message =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Hi"})
    resp = requests.post(config.url + 'message/share/v1', json={'token': pytest.user1.json()['token'], 'og_message_id': message.json()['message_id'], 'message':"YO", 'channel_id': pytest.channel2.json()['channel_id'], 'dm_id': -1})
    assert resp.status_code == AccessError.code

def test_send_to_invalid_dm(clear_and_register):
    message =  requests.post(config.url + 'message/senddm/v1', json={'token':pytest.user1.json()['token'],'dm_id':pytest.dm1.json()['dm_id'],'message':"Hi"})
    resp = requests.post(config.url + 'message/share/v1', json={'token': pytest.user1.json()['token'], 'og_message_id': message.json()['message_id'], 'message':"YO", 'channel_id': -1, 'dm_id': pytest.dm2.json()['dm_id']})
    assert resp.status_code == AccessError.code

def test_normal_function_channel(clear_and_register):
    requests.post(config.url + 'channel/join/v2', json={'token': pytest.user2.json()['token'], 'channel_id': pytest.channel1.json()['channel_id']})
    message =  requests.post(config.url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':pytest.channel1.json()['channel_id'],'message':"Hi"})
    resp = requests.post(config.url + 'message/share/v1', json={'token': pytest.user2.json()['token'], 'og_message_id': message.json()['message_id'], 'message':"YO", 'channel_id': pytest.channel1.json()['channel_id'], 'dm_id': -1})
    assert resp.status_code == 200

def test_normal_function_dm(clear_and_register):
    message =  requests.post(config.url + 'message/senddm/v1', json={'token':pytest.user1.json()['token'],'dm_id':pytest.dm1.json()['dm_id'],'message':"Hi"})
    resp = requests.post(config.url + 'message/share/v1', json={'token': pytest.user1.json()['token'], 'og_message_id': message.json()['message_id'], 'message':"YO", 'channel_id': -1, 'dm_id': pytest.dm1.json()['dm_id']})
    assert resp.status_code == 200