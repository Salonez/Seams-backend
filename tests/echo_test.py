# import pytest

# from src.echo import echo
# from src.error import InputError


# def test_echo():
#     assert echo("1") == "1", "1 == 1"
#     assert echo("abc") == "abc", "abc == abc"
#     assert echo("trump") == "trump", "trump == trump"


# def test_echo_except():
#     with pytest.raises(InputError):
#         assert echo("echo")

import pytest
import requests
import json
from src import config
from src.error import InputError

def test_echo():
    '''
    A simple test to check echo
    '''
    resp = requests.get(config.url + 'echo', params={'data': 'hello'})
    assert json.loads(resp.text) == {'data': 'hello'}
    resp = requests.get(config.url + 'echo', params={'data': 'echo'})
    assert resp.status_code == InputError.code

