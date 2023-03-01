import pytest
import requests
import time

from src import config

from src.error import *

@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')
    pytest.user1 = requests.post(config.url + 'auth/register/v2', json={'email': 'test@test.com', 'password': 'password', 'name_first': 'Nick', 'name_last': 'Decsease'})
    pytest.user2 = requests.post(config.url + 'auth/register/v2', json={'email': 'testadmin@test.com', 'password': 'password', 'name_first': 'Nicholas', 'name_last': 'Decsease'})
    pytest.dm1 = requests.post(config.url + 'dm/create/v1', json={'token': pytest.user1.json()['token'], 'u_ids': [2]})
    pytest.dm2 = requests.post(config.url + 'dm/create/v1', json={'token': pytest.user1.json()['token'], 'u_ids': []})
    return

def test_2second(clear_and_register):
    message =  requests.post(config.url + 'message/sendlaterdm/v1', json={'token':pytest.user1.json()['token'],'dm_id':pytest.dm1.json()['dm_id'],'message':"Test", 'time_sent': int(time.time())+2 })
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'] })
    assert resp.status_code == InputError.code
    time.sleep(3)
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'] })
    assert resp.status_code == 200

def test_0delay(clear_and_register):
    message =  requests.post(config.url + 'message/sendlaterdm/v1', json={'token':pytest.user1.json()['token'],'dm_id':pytest.dm1.json()['dm_id'],'message':"Test", 'time_sent': int(time.time()) })
    time.sleep(1)
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': pytest.user1.json()['token'], 'message_id': message.json()['message_id'] })
    assert resp.status_code == 200

def test_time_sent_past(clear_and_register):
    message =  requests.post(config.url + 'message/sendlaterdm/v1', json={'token':pytest.user1.json()['token'],'dm_id':pytest.dm1.json()['dm_id'],'message':"Test", 'time_sent': 0 })
    assert message.status_code == InputError.code

def test_channel_doesnt_exsist(clear_and_register):
    message =  requests.post(config.url + 'message/sendlaterdm/v1', json={'token':pytest.user1.json()['token'],'dm_id': 0,'message':"Test", 'time_sent': int(time.time())})
    assert message.status_code == InputError.code

def test_empty_message(clear_and_register):
    message =  requests.post(config.url + 'message/sendlaterdm/v1', json={'token':pytest.user1.json()['token'],'dm_id':pytest.dm1.json()['dm_id'],'message':"", 'time_sent': int(time.time()) })
    assert message.status_code == InputError.code

def test_too_large_message(clear_and_register):
    message =  requests.post(config.url + 'message/sendlaterdm/v1', json={'token':pytest.user1.json()['token'],'dm_id':pytest.dm1.json()['dm_id'],'message':"Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Na", 'time_sent': int(time.time()) })
    assert message.status_code == InputError.code

def test_user_not_member(clear_and_register):
    message =  requests.post(config.url + 'message/sendlaterdm/v1', json={'token':pytest.user2.json()['token'],'dm_id':pytest.dm2.json()['dm_id'],'message':"lol", 'time_sent': int(time.time()) })
    assert message.status_code == AccessError.code
