import pytest
from src.error import *
import requests
import json
from src import config
from tests.helpers import clear
import time

@pytest.fixture
def global_own():
    clear()
    # global_owner = requests.post(config.url + 'auth/register/v2', json={'email': 'coverage@gmail.com', 'password': '1234567', 'name_first': 'Cover', 'name_last': 'Age'})
    # requests.post(config.url + 'channels/create/v2', json={'token': global_owner.json()['token'], 'name': 'Coverage channel', 'is_public': True})
    # return global_owner

def test_invalid_user(global_own):
    invalid_user = 9999
    resp = requests.get(config.url + 'user/stats/v1', params={'token': invalid_user})
    assert resp.status_code == 403

def test_user_with_no_channels_or_dms_joined(global_own):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    resp = requests.get(config.url + 'user/stats/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '"channels_joined": [{"num_channels_joined": 0, "time_stamp": ' in resp
    assert '"dms_joined": [{"num_dms_joined": 0, "time_stamp": ' in resp
    assert  '"messages_sent": [{"num_messages_sent": 0, "time_stamp": ' in resp
    assert '"involvement_rate": 0' in resp

def test_user_creates_channel_and_in_no_dms(global_own):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    requests.post(config.url + 'channels/create/v2', json={'token': user.json()['token'], 'name': 'Coverage channel', 'is_public': True})
    resp = requests.get(config.url + 'user/stats/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '{"num_channels_joined": 0, "time_stamp": ' in resp
    assert '{"num_channels_joined": 1, "time_stamp": ' in resp
    assert '{"num_dms_joined": 0, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 0, "time_stamp": ' in resp
    assert '"involvement_rate": 1' in resp

def test_user_joins_2_channels(global_own):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    creator = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'testchannel', 'is_public': True})
    requests.post(config.url + 'channel/join/v2', json={'token': user.json()['token'], 'channel_id': channel.json()['channel_id']})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': user.json()['token'], 'name': 'testchannel1', 'is_public': True})
    resp = requests.get(config.url + 'user/stats/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '{"num_channels_joined": 0, "time_stamp": ' in resp
    assert '{"num_channels_joined": 1, "time_stamp": ' in resp
    assert '{"num_channels_joined": 2, "time_stamp": ' in resp
    assert '{"num_dms_joined": 0, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 0, "time_stamp": ' in resp
    assert '"involvement_rate": 1' in resp

def test_user_invited_to_channel_and_messages(global_own):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    creator = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'testchannel', 'is_public': True})
    requests.post(config.url + 'channel/invite/v2', json={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': user.json()['auth_user_id']})
    requests.post(config.url + 'message/send/v1', json={'token':user.json()['token'],'channel_id':channel.json()['channel_id'],'message':"Test"})
    resp = requests.get(config.url + 'user/stats/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '{"num_channels_joined": 0, "time_stamp": ' in resp
    assert '{"num_channels_joined": 1, "time_stamp": ' in resp
    assert '{"num_dms_joined": 0, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 0, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 1, "time_stamp": ' in resp
    assert '"involvement_rate": 1' in resp

def test_user_with_no_channel_but_has_dm_messages(global_own):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    dm_user = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':user.json()['token'], 'u_ids': [dm_user.json()['auth_user_id']]})
    requests.post(config.url + 'message/senddm/v1', json={'token':user.json()['token'],'dm_id':dm1.json()['dm_id'],'message':"Test"})
    resp = requests.get(config.url + 'user/stats/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '{"num_channels_joined": 0, "time_stamp": ' in resp
    assert '{"num_dms_joined": 0, "time_stamp": ' in resp
    assert '{"num_dms_joined": 1, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 0, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 1, "time_stamp": ' in resp
    assert '"involvement_rate": 1' in resp

def test_involvement(global_own):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    dm_user = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':dm_user.json()['token'], 'u_ids': [user.json()['auth_user_id']]})
    requests.post(config.url + 'message/senddm/v1', json={'token':user.json()['token'],'dm_id':dm1.json()['dm_id'],'message':"Test"})
    creator = requests.post(config.url + 'auth/register/v2', json={'email': 'test1@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'testchannel', 'is_public': True})
    resp = requests.get(config.url + 'user/stats/v1', params={'token': user.json()['token']})
    involvement = 2/3
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '{"num_channels_joined": 0, "time_stamp": ' in resp
    assert '{"num_dms_joined": 0, "time_stamp": ' in resp
    assert '{"num_dms_joined": 1, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 0, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 1, "time_stamp": ' in resp
    assert f'"involvement_rate": {involvement}' in resp

def test_user_joins_then_leaves_both_channel_and_dm(global_own):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    dm_user = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':user.json()['token'], 'u_ids': [dm_user.json()['auth_user_id']]})
    requests.post(config.url + 'message/senddm/v1', json={'token':user.json()['token'],'dm_id':dm1.json()['dm_id'],'message':"Test"})
    requests.post(config.url + 'dm/leave/v1', json={'token':user.json()['token'], 'dm_id': dm1.json()['dm_id']})
    creator = requests.post(config.url + 'auth/register/v2', json={'email': 'test1@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'testchannel', 'is_public': True})
    requests.post(config.url + 'channel/invite/v2', json={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': user.json()['auth_user_id']})
    requests.post(config.url + 'channel/leave/v1', json={'token': user.json()['token'], 'channel_id': channel.json()['channel_id']})
    resp = requests.get(config.url + 'user/stats/v1', params={'token': user.json()['token']})
    involvement = 1/3
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    print(resp)
    assert '{"num_channels_joined": 0, "time_stamp": ' in resp
    assert '{"num_channels_joined": 1, "time_stamp": ' in resp
    assert '{"num_dms_joined": 0, "time_stamp": ' in resp
    assert '{"num_dms_joined": 1, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 0, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 1, "time_stamp": ' in resp
    assert f'"involvement_rate": {involvement}' in resp

def test_dm_owner_and_dm_user(global_own):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    dm_user = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':user.json()['token'], 'u_ids': [dm_user.json()['auth_user_id']]})
    requests.post(config.url + 'message/senddm/v1', json={'token':user.json()['token'],'dm_id':dm1.json()['dm_id'],'message':"Test"})
    requests.post(config.url + 'dm/leave/v1', json={'token':user.json()['token'], 'dm_id': dm1.json()['dm_id']})
    resp = requests.get(config.url + 'user/stats/v1', params={'token': user.json()['token']})
    involvement = 1/2
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '{"num_channels_joined": 0, "time_stamp": ' in resp
    assert '{"num_dms_joined": 0, "time_stamp": ' in resp
    assert '{"num_dms_joined": 1, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 0, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 1, "time_stamp": ' in resp
    assert f'"involvement_rate": {involvement}' in resp
    resp1 = requests.get(config.url + 'user/stats/v1', params={'token': user.json()['token']})
    assert resp1.status_code == 200
    resp1 = json.dumps(json.loads(resp1.text))
    assert '{"num_channels_joined": 0, "time_stamp": ' in resp1
    assert '{"num_dms_joined": 0, "time_stamp": ' in resp1
    assert '{"num_dms_joined": 1, "time_stamp": ' in resp1
    assert  '{"num_messages_sent": 0, "time_stamp": ' in resp1

def test_dm_remove(global_own):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    dm_user = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':user.json()['token'], 'u_ids': [dm_user.json()['auth_user_id']]})
    requests.delete(config.url + 'dm/remove/v1', json={'token':user.json()['token'], 'dm_id': dm1.json()['dm_id']})
    resp = requests.get(config.url + 'user/stats/v1', params={'token': dm_user.json()['token']})
    involvement = 0
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '{"num_channels_joined": 0, "time_stamp": ' in resp
    assert '{"num_dms_joined": 0, "time_stamp": ' in resp
    assert '{"num_dms_joined": 1, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 0, "time_stamp": ' in resp
    assert f'"involvement_rate": {involvement}' in resp

def test_dm_and_channel_standup_and_send_later(global_own):
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'amazon@gmail.com', 'password': '1234567', 'name_first': 'Jeff', 'name_last': 'Bezos'})
    creator = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    channel = requests.post(config.url + 'channels/create/v2', json={'token': creator.json()['token'], 'name': 'testchannel', 'is_public': True})
    requests.post(config.url + 'channel/invite/v2', json={'token': creator.json()['token'], 'channel_id': channel.json()['channel_id'], 'u_id': user.json()['auth_user_id']})
    requests.post(config.url + 'standup/start/v1', json={  'token':user.json()['token'], 'channel_id': channel.json()['channel_id'],'length': 0.25})
    requests.post(config.url + 'standup/send/v1',json={'token':creator.json()['token'], 'channel_id': channel.json()['channel_id'],'message':"I am a message"})
    requests.post(config.url + 'standup/send/v1',json={'token':user.json()['token'], 'channel_id': channel.json()['channel_id'],'message':"I am a message too!"})
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token':creator.json()['token'], 'u_ids': [user.json()['auth_user_id']]})
    requests.post(config.url + 'message/sendlater/v1', json={'token':user.json()['token'],'channel_id':channel.json()['channel_id'],'message': f"messaging lol", 'time_sent': int(time.time())+0.25 })
    requests.post(config.url + 'message/sendlaterdm/v1', json={'token':user.json()['token'],'dm_id':dm1.json()['dm_id'],'message':f"01234567890123456789", 'time_sent': int(time.time())+0.25 })
    time.sleep(2)
    resp = requests.get(config.url + 'user/stats/v1', params={'token': user.json()['token']})
    assert resp.status_code == 200
    resp = json.dumps(json.loads(resp.text))
    assert '{"num_channels_joined": 0, "time_stamp": ' in resp
    assert '{"num_channels_joined": 1, "time_stamp": ' in resp
    assert '{"num_dms_joined": 0, "time_stamp": ' in resp
    assert '{"num_dms_joined": 1, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 0, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 1, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 2, "time_stamp": ' in resp
    assert  '{"num_messages_sent": 3, "time_stamp": ' in resp
    assert '"involvement_rate": 1' in resp