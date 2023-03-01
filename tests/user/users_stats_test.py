import pytest
from src.error import *
import requests
import json
from src import config
from tests.helpers import clear
import time

@pytest.fixture
def clear_and_register():
    clear()

def test_invalid_user(clear_and_register):
    invalid_user = 9999
    resp = requests.get(config.url + 'user/stats/v1', params={'token': invalid_user})
    assert resp.status_code == 403

def test_no_channels_or_dms(clear_and_register):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    resp = requests.get(config.url + 'users/stats/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '"channels_exist": [{"num_channels_exist": 0, ' in resp
    assert '"dms_exist": [{"num_dms_exist": 0, ' in resp
    assert '"messages_exist": [{"num_messages_exist": 0, ' in resp
    assert '"utilization_rate": 0' in resp

def test_one_channel(clear_and_register):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    requests.post(config.url + 'channels/create/v2', json={'token': user.json()['token'], 'name': 'Test channel', 'is_public': True})
    resp = requests.get(config.url + 'users/stats/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '{"num_channels_exist": 0, ' in resp
    assert '{"num_channels_exist": 1, ' in resp
    assert '"dms_exist": [{"num_dms_exist": 0, ' in resp
    assert '"messages_exist": [{"num_messages_exist": 0, ' in resp
    assert '"utilization_rate": 1' in resp

def test_one_dm(clear_and_register):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    dm_user = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':user.json()['token'], 'u_ids': [dm_user.json()['auth_user_id']]})
    requests.post(config.url + 'message/senddm/v1', json={'token':user.json()['token'],'dm_id':dm1.json()['dm_id'],'message':"Test"})
    resp = requests.get(config.url + 'users/stats/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '{"num_channels_exist": 0, ' in resp
    assert '"dms_exist": [{"num_dms_exist": 0, ' in resp
    assert '{"num_dms_exist": 1, ' in resp
    assert '"messages_exist": [{"num_messages_exist": 0, ' in resp
    assert '{"num_messages_exist": 1, ' in resp
    assert '"utilization_rate": 1' in resp

def test_channels_and_dms_messages_and_involvement(clear_and_register):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    requests.post(config.url + 'channels/create/v2', json={'token': user.json()['token'], 'name': 'Test channel', 'is_public': True})
    dm_user = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':user.json()['token'], 'u_ids': [dm_user.json()['auth_user_id']]})
    requests.post(config.url + 'message/senddm/v1', json={'token':user.json()['token'],'dm_id':dm1.json()['dm_id'],'message':"Test"})
    requests.post(config.url + 'dm/leave/v1', json={'token':dm_user.json()['token'], 'dm_id': dm1.json()['dm_id']})
    resp = requests.get(config.url + 'users/stats/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    utilization = 1/2
    assert '{"num_channels_exist": 0, ' in resp
    assert '{"num_channels_exist": 1, ' in resp
    assert '"dms_exist": [{"num_dms_exist": 0, ' in resp
    assert '{"num_dms_exist": 1, ' in resp
    assert '"messages_exist": [{"num_messages_exist": 0, ' in resp
    assert '{"num_messages_exist": 1, ' in resp
    assert f'"utilization_rate": {utilization}' in resp

def test_removal_of_dm_messages_and_channel_messages(clear_and_register):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    dm_user = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':user.json()['token'], 'u_ids': [dm_user.json()['auth_user_id']]})
    dm_msg = requests.post(config.url + 'message/senddm/v1', json={'token':user.json()['token'],'dm_id':dm1.json()['dm_id'],'message':"Test"})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': user.json()['token'], 'name': 'Test channel', 'is_public': True})
    channel_msg =  requests.post(config.url + 'message/send/v1', json={'token': user.json()['token'],'channel_id': channel.json()['channel_id'],'message':"Test"})
    requests.delete(config.url + 'message/remove/v1', json={'token': user.json()['token'], 'message_id': dm_msg.json()['message_id']})
    requests.delete(config.url + 'message/remove/v1', json={'token': user.json()['token'], 'message_id': channel_msg.json()['message_id']})
    resp = requests.get(config.url + 'users/stats/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '{"num_channels_exist": 0, ' in resp
    assert '{"num_channels_exist": 1, ' in resp
    assert '"dms_exist": [{"num_dms_exist": 0, ' in resp
    assert ', {"num_dms_exist": 1, ' in resp
    assert '"messages_exist": [{"num_messages_exist": 0, ' in resp
    assert ', {"num_messages_exist": 1, ' in resp
    assert ', {"num_messages_exist": 0, ' in resp
    assert '"utilization_rate": 1' in resp

def test_removal_dm_with_messages(clear_and_register):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    dm_user = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':user.json()['token'], 'u_ids': [dm_user.json()['auth_user_id']]})
    requests.post(config.url + 'message/senddm/v1', json={'token':user.json()['token'],'dm_id':dm1.json()['dm_id'],'message':"Test"})
    requests.post(config.url + 'message/senddm/v1', json={'token':user.json()['token'],'dm_id':dm1.json()['dm_id'],'message':"Let's finish this"})
    requests.delete(config.url + 'dm/remove/v1', json={'token': user.json()['token'], 'dm_id': dm1.json()['dm_id']})
    resp = requests.get(config.url + 'users/stats/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '{"num_channels_exist": 0, ' in resp
    assert '"dms_exist": [{"num_dms_exist": 0, ' in resp
    assert ', {"num_dms_exist": 1, ' in resp
    assert ', {"num_dms_exist": 0, ' in resp
    assert '"messages_exist": [{"num_messages_exist": 0, ' in resp
    assert ', {"num_messages_exist": 1, ' in resp
    assert ', {"num_messages_exist": 2, ' in resp
    assert ', {"num_messages_exist": 0, ' in resp
    assert '"utilization_rate": 0' in resp

# def test_standup_and_send_later(clear_and_register):
#     creator = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
#     channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'Test channel', 'is_public': True})
#     user = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
#     requests.post(config.url + 'channel/invite/v2', json={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': user.json()['auth_user_id']})
#     requests.post(config.url + 'standup/start/v1', json={  'token':user.json()['token'], 'channel_id': channel.json()['channel_id'],'length': 0.25})
#     requests.post(config.url + 'standup/send/v1',json={'token':creator.json()['token'], 'channel_id': channel.json()['channel_id'],'message':"I am a message"})
#     requests.post(config.url + 'standup/send/v1',json={'token':user.json()['token'], 'channel_id': channel.json()['channel_id'],'message':"I am a message too!"})
#     dm1 = requests.post(config.url + 'dm/create/v1', json={'token':creator.json()['token'], 'u_ids': [user.json()['auth_user_id']]})
#     requests.post(config.url + 'message/sendlater/v1', json={'token':user.json()['token'],'channel_id':channel.json()['channel_id'],'message': f"messaging lol", 'time_sent': int(time.time())+0.25 })
#     requests.post(config.url + 'message/sendlaterdm/v1', json={'token':creator.json()['token'],'dm_id':dm1.json()['dm_id'],'message':f"01234567890123456789", 'time_sent': int(time.time())+0.25 })
#     time.sleep(2)
#     resp = requests.get(config.url + 'users/stats/v1', params={'token': user.json()['token']})
#     assert resp.status_code == 200
#     resp = json.dumps(json.loads(resp.text))
#     utilization = 1
#     assert '{"num_channels_exist": 0, ' in resp
#     assert '{"num_channels_exist": 1, ' in resp
#     assert '"dms_exist": [{"num_dms_exist": 0, ' in resp
#     assert ', {"num_dms_exist": 1, ' in resp
#     assert '"messages_exist": [{"num_messages_exist": 0, ' in resp
#     assert ', {"num_messages_exist": 1, ' in resp
#     assert ', {"num_messages_exist": 2, ' in resp
#     assert ', {"num_messages_exist": 3, ' in resp
#     assert f'"utilization_rate": {utilization}' in resp
