import requests
import pytest
from tests.helpers import clear
from src.config import url
from src.error import InputError


TEST_PASSWORD = 'bestpasswordever123'
TEST_NAME_FIRST = 'Steve'
TEST_NAME_LAST = 'Jobs'

@pytest.fixture
def clear_and_register():
    clear()
    pytest.pretestuser = requests.post(
        url + '/auth/register/v2',
        json={
            "email": "abc@def.com",
            "password": TEST_PASSWORD,
            "name_first": "another",
            "name_last": "name"
        }
    )
    pytest.user1 = requests.post(
        url + '/auth/register/v2',
        json={
            "email": "steve@steve.com",
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    )
    pytest.user2 = requests.post(
        url + '/auth/register/v2',
        json={
            "email": "bill@gates.com",
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    )
    pytest.user3 = requests.post(
        url + '/auth/register/v2',
        json={
            "email": "elonmusk@apple.com",
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    )
    pytest.posttestuser = requests.post(
        url + '/auth/register/v2',
        json={
            "email": "abcdef@def.com",
            "password": TEST_PASSWORD,
            "name_first": "another",
            "name_last": "name"
        }
    )



def test_search_query_str_character_length(clear_and_register):
    resp = requests.get(url + 'search/v1', params={'token': pytest.user1.json()['token'], 'query_str': ''})
    assert resp.status_code == InputError.code

    resp = requests.get(url + 'search/v1', params={'token': pytest.user1.json()['token'], 'query_str': 'a'*2000})
    assert resp.status_code == InputError.code


def test_search_successful(clear_and_register):
    # User 1 and 2
    dm1 = requests.post(url + 'dm/create/v1', json={'token': pytest.user1.json()['token'], 'u_ids': [pytest.user2.json()['auth_user_id']]})
    dm1_message1 = requests.post(url + 'message/senddm/v1', json={'token':pytest.user1.json()['token'],'dm_id':dm1.json()['dm_id'],'message':"Dm1TestMessage1"})
    dm1_message2 = requests.post(url + 'message/senddm/v1', json={'token':pytest.user1.json()['token'],'dm_id':dm1.json()['dm_id'],'message':"Dm1TestMessage2"})
    dm1_message3 = requests.post(url + 'message/senddm/v1', json={'token':pytest.user2.json()['token'],'dm_id':dm1.json()['dm_id'],'message':"Dm1TestMessage3"})

    # User 2 and User 3
    dm2 = requests.post(url + 'dm/create/v1', json={'token': pytest.user2.json()['token'], 'u_ids': [pytest.user3.json()['auth_user_id']]})
    dm2_message1 = requests.post(url + 'message/senddm/v1', json={'token':pytest.user2.json()['token'],'dm_id':dm2.json()['dm_id'],'message':"Dm2TestMessage1"})
    dm2_message2 = requests.post(url + 'message/senddm/v1', json={'token':pytest.user2.json()['token'],'dm_id':dm2.json()['dm_id'],'message':"Dm2TestMessage2"})
    dm2_message3 = requests.post(url + 'message/senddm/v1', json={'token':pytest.user3.json()['token'],'dm_id':dm2.json()['dm_id'],'message':"Dm2TestMessage3"})

    # User 1 and 3
    channel1 = requests.post(url + 'channels/create/v2', json={'token': pytest.user1.json()['token'], 'name': 'TestChannel1', 'is_public': True})
    requests.post(url + 'channel/join/v2', json={'token': pytest.user3.json()['token'], 'channel_id': channel1.json()['channel_id']})
    channel1_message1 = requests.post(url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':channel1.json()['channel_id'],'message':"Channel1TestMessage1"})
    channel1_message2 = requests.post(url + 'message/send/v1', json={'token':pytest.user1.json()['token'],'channel_id':channel1.json()['channel_id'],'message':"Channel1TestMessage2"})
    channel1_message3 = requests.post(url + 'message/send/v1', json={'token':pytest.user3.json()['token'],'channel_id':channel1.json()['channel_id'],'message':"Channel1TestMessage3"})

    # User 3 and 2
    channel2 = requests.post(url + 'channels/create/v2', json={'token': pytest.user3.json()['token'], 'name': 'TestChannel2', 'is_public': True})
    requests.post(url + 'channel/join/v2', json={'token': pytest.user2.json()['token'], 'channel_id': channel2.json()['channel_id']})
    channel2_message1 = requests.post(url + 'message/send/v1', json={'token':pytest.user3.json()['token'],'channel_id':channel2.json()['channel_id'],'message':"Channel2TestMessage1"})
    channel2_message2 = requests.post(url + 'message/send/v1', json={'token':pytest.user3.json()['token'],'channel_id':channel2.json()['channel_id'],'message':"Channel2TestMessage2"})
    channel2_message3 = requests.post(url + 'message/send/v1', json={'token':pytest.user2.json()['token'],'channel_id':channel2.json()['channel_id'],'message':"Channel2TestMessage3"})

    # User 1 Searches (1)
    resp = requests.get(
        url + 'search/v1',
        params={
            'token': pytest.user1.json()['token'],
            'query_str': 'testmessage1'
        }
    )

    assert resp.status_code == 200

    # Make sure there are no duplicates
    search_results_message_ids = [message['message_id'] for message in resp.json()['messages']]
    assert len(search_results_message_ids) == len(set(search_results_message_ids))

    assert set(search_results_message_ids) == {dm1_message1.json()['message_id'], channel1_message1.json()['message_id']}

    # User 1 Searches (2)
    resp = requests.get(
        url + 'search/v1',
        params={
            'token': pytest.user1.json()['token'],
            'query_str': 'dm1'
        }
    )

    assert resp.status_code == 200

    # Make sure there are no duplicates
    search_results_message_ids = [message['message_id'] for message in resp.json()['messages']]
    assert len(search_results_message_ids) == len(set(search_results_message_ids))

    assert set(search_results_message_ids) == {dm1_message1.json()['message_id'], dm1_message2.json()['message_id'], dm1_message3.json()['message_id']}

    # User 1 Searches (3)
    resp = requests.get(
        url + 'search/v1',
        params={
            'token': pytest.user1.json()['token'],
            'query_str': 'testmessage'
        }
    )

    assert resp.status_code == 200

    # Make sure there are no duplicates
    search_results_message_ids = [message['message_id'] for message in resp.json()['messages']]
    assert len(search_results_message_ids) == len(set(search_results_message_ids))

    assert set(search_results_message_ids) == {
        dm1_message1.json()['message_id'],
        dm1_message2.json()['message_id'],
        dm1_message3.json()['message_id'],
        channel1_message1.json()['message_id'],
        channel1_message2.json()['message_id'],
        channel1_message3.json()['message_id']
    }

    # User 2 Searches (1)
    resp = requests.get(
        url + 'search/v1',
        params={
            'token': pytest.user2.json()['token'],
            'query_str': 'testmessage2'
        }
    )

    assert resp.status_code == 200

    # Make sure there are no duplicates
    search_results_message_ids = [message['message_id'] for message in resp.json()['messages']]
    assert len(search_results_message_ids) == len(set(search_results_message_ids))

    assert set(search_results_message_ids) == {dm1_message2.json()['message_id'], dm2_message2.json()['message_id'], channel2_message2.json()['message_id']}

    # User 2 Searches (2)
    resp = requests.get(
        url + 'search/v1',
        params={
            'token': pytest.user2.json()['token'],
            'query_str': 'dm2'
        }
    )

    assert resp.status_code == 200

    # Make sure there are no duplicates
    search_results_message_ids = [message['message_id'] for message in resp.json()['messages']]
    assert len(search_results_message_ids) == len(set(search_results_message_ids))

    assert set(search_results_message_ids) == {dm2_message1.json()['message_id'], dm2_message2.json()['message_id'], dm2_message3.json()['message_id']}

    # User 2 Searches (3)
    resp = requests.get(
        url + 'search/v1',
        params={
            'token': pytest.user2.json()['token'],
            'query_str': 'testmessage'
        }
    )

    assert resp.status_code == 200

    # Make sure there are no duplicates
    search_results_message_ids = [message['message_id'] for message in resp.json()['messages']]
    assert len(search_results_message_ids) == len(set(search_results_message_ids))

    assert set(search_results_message_ids) == {
        dm1_message1.json()['message_id'],
        dm1_message2.json()['message_id'],
        dm1_message3.json()['message_id'],
        dm2_message1.json()['message_id'],
        dm2_message2.json()['message_id'],
        dm2_message3.json()['message_id'],
        channel2_message1.json()['message_id'],
        channel2_message2.json()['message_id'],
        channel2_message3.json()['message_id']
    }
    
    # User 3 Searches (1)
    resp = requests.get(
        url + 'search/v1',
        params={
            'token': pytest.user3.json()['token'],
            'query_str': 'testmessage3'
        }
    )

    assert resp.status_code == 200

    # Make sure there are no duplicates
    search_results_message_ids = [message['message_id'] for message in resp.json()['messages']]
    assert len(search_results_message_ids) == len(set(search_results_message_ids))

    assert set(search_results_message_ids) == {dm2_message3.json()['message_id'], channel1_message3.json()['message_id'], channel2_message3.json()['message_id']}

    # User 3 Searches (2)
    resp = requests.get(
        url + 'search/v1',
        params={
            'token': pytest.user3.json()['token'],
            'query_str': 'dm2'
        }
    )

    assert resp.status_code == 200

    # Make sure there are no duplicates
    search_results_message_ids = [message['message_id'] for message in resp.json()['messages']]
    assert len(search_results_message_ids) == len(set(search_results_message_ids))

    assert set(search_results_message_ids) == {dm2_message1.json()['message_id'], dm2_message2.json()['message_id'], dm2_message3.json()['message_id']}

    # User 3 Searches (3)
    resp = requests.get(
        url + 'search/v1',
        params={
            'token': pytest.user3.json()['token'],
            'query_str': 'testmessage'
        }
    )

    assert resp.status_code == 200

    # Make sure there are no duplicates
    search_results_message_ids = [message['message_id'] for message in resp.json()['messages']]
    assert len(search_results_message_ids) == len(set(search_results_message_ids))

    assert set(search_results_message_ids) == {
        dm2_message1.json()['message_id'],
        dm2_message2.json()['message_id'],
        dm2_message3.json()['message_id'],
        channel1_message1.json()['message_id'],
        channel1_message2.json()['message_id'],
        channel1_message3.json()['message_id'],
        channel2_message1.json()['message_id'],
        channel2_message2.json()['message_id'],
        channel2_message3.json()['message_id']
    }

    # User 1 searches for messages that does not belong to him
    resp = requests.get(
        url + 'search/v1',
        params={
            'token': pytest.user1.json()['token'],
            'query_str': 'dm2testmessage2'
        }
    )

    assert resp.status_code == 200

    assert len(resp.json()['messages']) == 0

    # User 2 searches for messages that does not belong to him
    resp = requests.get(
        url + 'search/v1',
        params={
            'token': pytest.user2.json()['token'],
            'query_str': 'channel1'
        }
    )

    assert resp.status_code == 200

    assert len(resp.json()['messages']) == 0

    # User 3 searches for messages that does not belong to him
    resp = requests.get(
        url + 'search/v1',
        params={
            'token': pytest.user3.json()['token'],
            'query_str': 'dm1'
        }
    )

    assert resp.status_code == 200

    assert len(resp.json()['messages']) == 0
