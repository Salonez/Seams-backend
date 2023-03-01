import pytest
import requests
import time
from src import config
from src.error import *
from src.data_store import data_store
from tests.helpers import clear

@pytest.fixture
def clear_and_register():
    clear()
    pytest.creator = requests.post(config.url + 'auth/register/v2',
        json={  'email': 'testemailcreate@gmail.com',
                'password': 'password',
                'name_first': 'John',
                'name_last': 'Sea'})
    pytest.user1 = requests.post(config.url + 'auth/register/v2',
        json={  'email': 'testemail1@gmail.com',
                'password': 'password',
                'name_first': 'Ron',
                'name_last': 'Swanson'})
    pytest.user2 = requests.post(config.url + 'auth/register/v2',
        json={  'email': 'testemail2@gmail.com',
                'password': 'password',
                'name_first': 'Steve',
                'name_last': 'Jobs'})
    pytest.user3 = requests.post(config.url + 'auth/register/v2',
        json={  'email': 'testemail3@gmail.com',
                'password': 'password',
                'name_first': 'Bob',
                'name_last': 'Bobson'})
    pytest.channel1 = requests.post(config.url + 'channels/create/v2',
        json={  'token': pytest.creator.json()['token'],
                'name': 'something',
                'is_public' : True})
    pytest.channel2 = requests.post(config.url + 'channels/create/v2',
        json={  'token': pytest.creator.json()['token'],
                'name': 'hello',
                'is_public' : False})
    requests.post(config.url + 'channel/join/v2',
        json={  'token': pytest.user2.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id']})

def test_invalid_id(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token': -1,
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    assert resp.status_code == 403

def test_invalid_channel_id(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'],
                'channel_id': -1,
                'length': 5})
    assert resp.status_code == 400

def test_negative_length(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': -5})
    assert resp.status_code == 400

def test_already_active_standup(clear_and_register):
    requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.user2.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    assert resp.status_code == 400

def test_not_member_of_channel(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.user1.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    assert resp.status_code == 403

def test_creates_standup_public(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    resp_data = resp.json()
    assert resp_data.keys() == {'time_finish'}

def test_creates_standup_private(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'],
                'channel_id': pytest.channel2.json()['channel_id'],
                'length': 5})
    resp_data = resp.json()
    assert resp_data.keys() == {'time_finish'}

def test_creates_standup_not_creator(clear_and_register):
    resp = requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.user2.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 5})
    resp_data = resp.json()
    assert resp_data.keys() == {'time_finish'}

def test_standup_added_as_channel_message(clear_and_register):
    requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 1})
    requests.post(config.url + 'standup/send/v1',
            json={'token':pytest.user2.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'message': 'happy birthday'})
    requests.post(config.url + 'standup/send/v1',
            json={'token':pytest.creator.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'message': 'hello'})
    time.sleep(2)
    resp = requests.get(config.url + 'channel/messages/v2',
            params={'token':pytest.user2.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'start': 0})
    resp_data = resp.json()
    store = data_store.get()
    print(resp_data)
    assert resp_data['messages'][0]['message'] == 'stevejobs: happy birthday\njohnsea: hello'
    assert store['standups'] == []
    
def test_over_1000(clear_and_register):
    requests.post(config.url + 'standup/start/v1',
            json={'token':pytest.creator.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'length': 1})
    requests.post(config.url + 'standup/send/v1',
            json={'token':pytest.user2.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'message': "According to all known laws of aviation, there is no way a bee should be able to fly. \
Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees don't care what humans think is impossible.\
 Yellow, black. Yellow, black. Yellow, black. Yellow, black. Ooh, black and yellow! Let's shake it up a little. Barry! Breakfast is ready! Ooming!\
  Hang on a second. Hello? - Barry? - Adam? - Oan you believe this is happening? - I can't. I'll pick you up. Looking sharp. Use the stairs. \
  Your father paid good money for those. Sorry. I'm excited. Here's the graduate. We're very proud of you, son. A perfect report card, all B's. Very proud.\
   Ma! I got a thing going here. - You got lint on your fuzz. - Ow! That's me! - Wave to us! We'll be in row 118,000. - Bye! Barry, I told you, "})
    requests.post(config.url + 'standup/send/v1',
            json={'token':pytest.creator.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'message': "No.2 to all known laws of aviation, there is no way a bee should be able to fly. \
Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees don't care what humans think is impossible.\
 Yellow, black. Yellow, black. Yellow, black.dethbrht rth ry uwse ggn j, black and yellow! Let's shake it up a little. Barry! Breakfast is ready! Ooming!\
  Hang on a second. Hello? - Barry? - Adam? - Oan you believe this is happening? - I can't. I'll pick you up. Looking sharp. Use the stairs. \
  Your father paid good money for those. Sorry. I'm excited. Here's the graduate. We're very proud of you, son. A perfect report card, all B's. Very proud.\
   Ma! I got a thing going here. - You got lint on your fuzz. - Ow! That's me! - Wave to us! We'll be in row 118,000. - Bye! Barry, I told you,"})
    time.sleep(2)
    resp = requests.get(config.url + 'channel/messages/v2',
            params={'token':pytest.user2.json()['token'],
                'channel_id': pytest.channel1.json()['channel_id'],
                'start': 0})
    resp_data = resp.json()
    store = data_store.get()
    print(resp_data)
    assert isinstance(resp_data['messages'][0]['message'], str)
    assert store['standups'] == []