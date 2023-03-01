import requests
import pytest

from src.config import url
from tests.helpers import clear


@pytest.fixture
def clear_and_register():
    clear()

    pytest.user1 = requests.post(
        url + 'auth/register/v2',
        json={
            "email": "testemail@email.com",
            "password": "password123",
            "name_first": "Steve",
            "name_last": "Jobs"
        }
    ).json()

    pytest.user2 = requests.post(
        url + 'auth/register/v2',
        json={
            "email": "testemail2@email.com",
            "password": "password123",
            "name_first": "Bill",
            "name_last": "Gates"
        }
    ).json()


def test_admin_userpermission_change_v1_invalid_user(clear_and_register):

    resp = requests.post(
        url + 'admin/userpermission/change/v1',
        json={
            "token": pytest.user1['token'],
            "u_id": 3,
            "permission_id": 1
        }
    )

    assert resp.status_code == 400

    # TODO: Test deleted user


def test_admin_userpermission_change_v1_demote_only_global_owner(clear_and_register):

    # Global Owner demote self
    resp = requests.post(
        url + 'admin/userpermission/change/v1',
        json={
            "token": pytest.user1['token'],
            "u_id": pytest.user1['auth_user_id'],
            "permission_id": 2
        }
    )

    assert resp.status_code == 400


def test_admin_userpermission_change_v1_permission_id_is_invalid(clear_and_register):

    resp = requests.post(
        url + 'admin/userpermission/change/v1',
        json={
            "token": pytest.user1['token'],
            "u_id": pytest.user2['auth_user_id'],
            "permission_id": 0
        }
    )

    assert resp.status_code == 400

    resp = requests.post(
        url + 'admin/userpermission/change/v1',
        json={
            "token": pytest.user1['token'],
            "u_id": pytest.user2['auth_user_id'],
            "permission_id": 3
        }
    )

    assert resp.status_code == 400


def test_admin_userpermission_change_v1_already_permission(clear_and_register):
    # Change own permission to same permission (1)
    resp = requests.post(
        url + 'admin/userpermission/change/v1',
        json={
            "token": pytest.user1['token'],
            "u_id": pytest.user1['auth_user_id'],
            "permission_id": 1
        }
    )

    assert resp.status_code == 400

    # Change other permission to same permission (1)
    resp = requests.post(
        url + 'admin/userpermission/change/v1',
        json={
            "token": pytest.user1['token'],
            "u_id": pytest.user2['auth_user_id'],
            "permission_id": 2
        }
    )

    assert resp.status_code == 400

    
    # Change user 2 to global owner for next test to work
    requests.post(
        url + 'admin/userpermission/change/v1',
        json={
            "token": pytest.user1['token'],
            "u_id": pytest.user2['auth_user_id'],
            "permission_id": 1
        }
    )

    resp = requests.post(
        url + 'admin/userpermission/change/v1',
        json={
            "token": pytest.user2['token'],
            "u_id": pytest.user2['auth_user_id'],
            "permission_id": 1
        }
    )

     # Change other permission to same permission (2)
    resp = requests.post(
        url + 'admin/userpermission/change/v1',
        json={
            "token": pytest.user2['token'],
            "u_id": pytest.user1['auth_user_id'],
            "permission_id": 1
        }
    )

    assert resp.status_code == 400


def test_admin_userpermission_change_v1_authorised_user_is_not_global_owner(clear_and_register):
    # User 2 (normal user) tries to change User 1 (Global Owner)
    resp = requests.post(
        url + 'admin/userpermission/change/v1',
        json={
            "token": pytest.user2['token'],
            "u_id": pytest.user1['auth_user_id'],
            "permission_id": 1
        }
    )

    assert resp.status_code == 403


def test_admin_userpermission_change_v1_authorised_user_successful(clear_and_register):
    resp = requests.post(
        url + 'admin/userpermission/change/v1',
        json={
            "token": pytest.user1['token'],
            "u_id": pytest.user2['auth_user_id'],
            "permission_id": 1
        }
    )

    assert resp.status_code == 200

    # User2 (who should have global permissions), will remove first user
    user_remove_resp = requests.delete(
        url + '/admin/user/remove/v1',
        json={
            "token": pytest.user2['token'],
            "u_id": pytest.user1['auth_user_id']
        }
    )

    assert user_remove_resp.status_code == 200
