import requests
import pytest
from PIL import Image, ImageChops

from tests.helpers import clear
from src.error import InputError
from src.config import url

TEST_EMAIL = 'steve@steve.com'
TEST_PASSWORD = 'bestpasswordever123'
TEST_NAME_FIRST = 'Steve'
TEST_NAME_LAST = 'Jobs'


@pytest.fixture
def clear_and_register():
    clear()
    pytest.pretestuser_json = requests.post(
        url + '/auth/register/v2',
        json={
            "email": "abc@def.com",
            "password": TEST_PASSWORD,
            "name_first": "another",
            "name_last": "name"
        }
    ).json()
    pytest.user1_json = requests.post(
        url + '/auth/register/v2',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name_first": TEST_NAME_FIRST,
            "name_last": TEST_NAME_LAST
        }
    ).json()
    pytest.posttestuser_json = requests.post(
        url + '/auth/register/v2',
        json={
            "email": "abcdef@def.com",
            "password": TEST_PASSWORD,
            "name_first": "another",
            "name_last": "name"
        }
    ).json()


def test_user_profile_uploadphoto_invalid_img_url(clear_and_register):
    # Test if url doesnt exist
    resp = requests.post(
        url + 'user/profile/uploadphoto/v1',
        json={
            "token": pytest.user1_json['token'],
            "img_url": "http://thisisarandomurlwhichnooneshouldhave10101231231313131.com/image.jpg",
            "x_start": 25,
            "y_start": 25,
            "x_end": 75,
            "y_end": 75
        }
    )

    assert resp.status_code == InputError.code


def test_user_profile_uploadphoto_invalid_img_dimensions(clear_and_register):
    # Test if dimensions are -1
    resp = requests.post(
        url + 'user/profile/uploadphoto/v1',
        json={
            "token": pytest.user1_json['token'],
            "img_url": "http://www.dolekemp96.org/about/bob/page2a.jpg",
            "x_start": -1,
            "y_start": -1,
            "x_end": 0,
            "y_end": 0
        }
    )

    assert resp.status_code == InputError.code

    resp = requests.post(
        url + 'user/profile/uploadphoto/v1',
        json={
            "token": pytest.user1_json['token'],
            "img_url": "http://www.dolekemp96.org/about/bob/page2a.jpg",
            "x_start": -2,
            "y_start": -2,
            "x_end": -1,
            "y_end": -1
        }
    )

    assert resp.status_code == InputError.code

    # Test if start and end dimensions are large values
    resp = requests.post(
        url + 'user/profile/uploadphoto/v1',
        json={
            "token": pytest.user1_json['token'],
            "img_url": "http://www.dolekemp96.org/about/bob/page2a.jpg",
            "x_start": 99999999999999999999999999999,
            "y_start": 99999999999999999999999999999,
            "x_end": 999999999999999999999999999999999,
            "y_end": 999999999999999999999999999999999
        }
    )

    assert resp.status_code == InputError.code

    # Test if only end dimensions are large values
    resp = requests.post(
        url + 'user/profile/uploadphoto/v1',
        json={
            "token": pytest.user1_json['token'],
            "img_url": "http://www.dolekemp96.org/about/bob/page2a.jpg",
            "x_start": 0,
            "y_start": 0,
            "x_end": 99999999999999999999999999999,
            "y_end": 99999999999999999999999999999
        }
    )

    assert resp.status_code == InputError.code


def test_user_profile_uploadphoto_end_dimensions_less_or_equal_to_start_dimensions(clear_and_register):
    resp = requests.post(
        url + 'user/profile/uploadphoto/v1',
        json={
            "token": pytest.user1_json['token'],
            "img_url": "http://www.dolekemp96.org/about/bob/page2a.jpg",
            "x_start": 50,
            "y_start": 50,
            "x_end": 45,
            "y_end": 60
        }
    )

    assert resp.status_code == InputError.code

    resp = requests.post(
        url + 'user/profile/uploadphoto/v1',
        json={
            "token": pytest.user1_json['token'],
            "img_url": "http://www.dolekemp96.org/about/bob/page2a.jpg",
            "x_start": 50,
            "y_start": 50,
            "x_end": 60,
            "y_end": 45
        }
    )

    assert resp.status_code == InputError.code

    resp = requests.post(
        url + 'user/profile/uploadphoto/v1',
        json={
            "token": pytest.user1_json['token'],
            "img_url": "http://www.dolekemp96.org/about/bob/page2a.jpg",
            "x_start": 50,
            "y_start": 50,
            "x_end": 50,
            "y_end": 45
        }
    )

    assert resp.status_code == InputError.code

    resp = requests.post(
        url + 'user/profile/uploadphoto/v1',
        json={
            "token": pytest.user1_json['token'],
            "img_url": "http://www.dolekemp96.org/about/bob/page2a.jpg",
            "x_start": 50,
            "y_start": 50,
            "x_end": 45,
            "y_end": 50
        }
    )

    assert resp.status_code == InputError.code


def test_user_profile_uploadphoto_is_not_jpg(clear_and_register):
    resp = requests.post(
        url + 'user/profile/uploadphoto/v1',
        json={
            "token": pytest.user1_json['token'],
            "img_url": "http://www.dolekemp96.org/about/bob/page2.html",
            "x_start": 0,
            "y_start": 0,
            "x_end": 50,
            "y_end": 50
        }
    )

    assert resp.status_code == InputError.code

    resp = requests.post(
        url + 'user/profile/uploadphoto/v1',
        json={
            "token": pytest.user1_json['token'],
            "img_url": "http://www.dolekemp96.org/menunewsroom.gif",
            "x_start": 0,
            "y_start": 0,
            "x_end": 50,
            "y_end": 50
        }
    )

    assert resp.status_code == InputError.code


def test_user_profile_uploadphoto_successful(clear_and_register):
    resp = requests.post(
        url + 'user/profile/uploadphoto/v1',
        json={
            "token": pytest.user1_json['token'],
            "img_url": "http://www.dolekemp96.org/about/bob/page2a.jpg",
            "x_start": 20,
            "y_start": 12,
            "x_end": 150,
            "y_end": 200
        }
    )

    assert resp.status_code == 200
    assert resp.json() == {}

    resp = requests.get(
            url + 'user/profile/v1',
            params={
                'token': pytest.user1_json['token'],
                'u_id': pytest.user1_json['auth_user_id']
            }
        )
    
    
    assert 'default_profile_photo' not in resp.json()['user']['profile_img_url']
