import pytest
import requests
from imapclient import IMAPClient
from src.error import InputError
import email
import time
import ssl

from src.config import url
from tests.helpers import clear

TEST_EMAIL = 'comp1531.t15b.dingo.test@gmail.com'
TEST_PASSWORD = 'bestpasswordever123'
TEST_NAME_FIRST = 'Steve'
TEST_NAME_LAST = 'Jobs'

GMAIL_HOST = 'imap.gmail.com'
RECIPIENT_USERNAME = 'comp1531.t15b.dingo.test@gmail.com'
RECIPIENT_PASSWORD = 'thegreatestpassword'

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

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


@pytest.fixture
def fixture_delete_all_mail_in_inbox():
    delete_all_mail_in_inbox()


def delete_all_mail_in_inbox():
    client = IMAPClient(GMAIL_HOST, use_uid=True, ssl_context=ssl_context)
    client.login(RECIPIENT_USERNAME, RECIPIENT_PASSWORD)
    client.select_folder('INBOX')

    UIDs = client.search('ALL')
    for UID in UIDs:
        client.delete_messages([UID])

    client.expunge()
    client.logout()

    # Wait for email deletion to take effect
    time.sleep(2)


@pytest.fixture
def request_password_reset():
    requests.post(
        url + '/auth/passwordreset/request/v1',
        json={
            'email': TEST_EMAIL
        }
    )


def get_reset_code_from_test_recipient_email():
    ## Connect, login and select the INBOX
    server = IMAPClient(GMAIL_HOST, use_uid=True, ssl_context=ssl_context)
    server.login(RECIPIENT_USERNAME, RECIPIENT_PASSWORD)
    server.select_folder('INBOX')

    messages = server.search(['FROM', 'comp1531.t15b.dingo@gmail.com'])
    for _, message_data in server.fetch(messages, 'RFC822').items():
        email_message = email.message_from_bytes(message_data[b'RFC822'], policy=email.policy.default)
        if email_message['Subject'] == 'Seams Reset Password':
            email_message.get_payload(0)
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    email_content = part.get_content()
                    reset_code = email_content.split(' ')[3]
                    server.logout()
                    return reset_code
    
    server.logout()
    return None


def test_auth_passwordreset_request_v1_invalid_email(clear_and_register):
    resp = requests.post(
        url + '/auth/passwordreset/request/v1',
        json={
            'email': 'randomemail1010101010@random.com'
        }
    )

    assert resp.status_code == 200
    assert resp.json() == {}


def test_auth_passwordreset_request_v1_successful(clear_and_register):
    delete_all_mail_in_inbox()
    requests.post(
        url + '/auth/passwordreset/request/v1',
        json={
            'email': 'abc@def.com'
        }
    )

    delete_all_mail_in_inbox()

    resp = requests.post(
        url + '/auth/passwordreset/request/v1',
        json={
            'email': TEST_EMAIL
        }
    )

    assert resp.status_code == 200
    assert resp.json() == {}

    # Wait for email to arrive
    time.sleep(3)
    reset_code = get_reset_code_from_test_recipient_email()
    assert reset_code is not None


def test_auth_passwordreset_reset_v1_invalid_random_reset_code(clear_and_register, fixture_delete_all_mail_in_inbox, request_password_reset):
    # Random reset code
    resp = requests.post(
        url + '/auth/passwordreset/reset/v1',
        json={
            'reset_code': 'f3f39f9384420348230',
            'new_password': 'abc123a'
        }
    )

    assert resp.status_code == InputError.code


def test_auth_passwordreset_reset_v1_invalid_used_reset_code(clear_and_register, fixture_delete_all_mail_in_inbox, request_password_reset):
   
    # Used reset code
    reset_code = get_reset_code_from_test_recipient_email()

    requests.post(
        url + '/auth/passwordreset/reset/v1',
        json={
            'reset_code': reset_code,
            'new_password': 'password123'
        }
    )

    resp = requests.post(
        url + '/auth/passwordreset/reset/v1',
        json={
            'reset_code': reset_code,
            'new_password': 'anewpassword123'
        }
    )

    assert resp.status_code == InputError.code


def test_auth_passwordreset_reset_v1_password_length(clear_and_register, fixture_delete_all_mail_in_inbox, request_password_reset):
    resp = requests.post(
        url + '/auth/passwordreset/reset/v1',
        json={
            'reset_code': get_reset_code_from_test_recipient_email(),
            'new_password': 'ab'
        }
    )

    assert resp.status_code == InputError.code


def test_auth_passwordreset_reset_v1_successful(clear_and_register, fixture_delete_all_mail_in_inbox, request_password_reset):
    time.sleep(2)
    resp = requests.post(
        url + '/auth/passwordreset/reset/v1',
        json={
            'reset_code': get_reset_code_from_test_recipient_email(),
            'new_password': 'password123'
        }
    )

    assert resp.status_code == 200
    assert resp.json() == {}

    login_user_resp = requests.post(
        url + '/auth/login/v2',
        json={
            "email": TEST_EMAIL,
            "password": 'password123'
        }
    )
    
    assert login_user_resp.status_code == 200
