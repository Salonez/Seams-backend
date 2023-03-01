import re
import hashlib
import math
import random
import yagmail
import time
from src.helpers import create_jwt_session_token, decode_jwt_session_token
from src.data_store import data_store
from src.error import InputError
from src.config import url


GMAIL_USERNAME = 'comp1531.t15b.dingo@gmail.com'
GMAIL_PASSWORD = 'thegreatestpassword'


def auth_login_v1(email, password):
    '''
    This function authenticates the user with the provided credentials.

    Arguments:
        email    (string)    - Email Address
        password (string)    - Password

    Exceptions:
        InputError
            - Occurs when any of:
                - email entered does not belong to a user
                - password is not correct

    Return Value:
        - auth_user_id  (integer)   - Authenticated User ID
        - token         (string)    - JWT Session Token
    '''

    # # Check parameter types
    # if not isinstance(email, str) or not isinstance(password, str):
    #     raise InputError('The provided parameter types are invalid.')

    store = data_store.get()

    # Check if the provided email is a registered email
    for user in store['users']:
        if user['email'] == email and user['removed'] == False:
            # Check if the provided password is correct
            if hashlib.sha256(password.encode()).hexdigest() == user['password']:

                # Generate JWT Session Token
                token = create_jwt_session_token(user['user_id'])

                return {
                    'auth_user_id': user['user_id'],
                    'token': token
                }

            raise InputError(description='Incorrect password.')
    
    raise InputError(description='This is not a registered email.')


def auth_register_v1(email, password, name_first, name_last):
    '''
    Registers a user

    Arguments:
        email          (string)     - Email Address
        password       (string)     - Password
        name_first     (string)     - First name
        name_last      (string)     - Last name
        ...

    Exceptions:
        InputError
            - Occurs when any of:
                - email entered is not a valid email
                - email address is already being used by another user
                - length of password is less than 6 characters
                - length of name_first is not between 1 and 50 characters inclusive
                - length of name_last is not between 1 and 50 characters inclusive

    Return Value:
        - auth_user_id  (integer)   - Authenticated User ID
        - token         (string)    - JWT Session Token
    '''

    # # Check parameter types
    # if \
    #     not isinstance(email, str) or \
    #     not isinstance(password, str) or \
    #     not isinstance(name_first, str) or \
    #     not isinstance(name_last, str) \
    # :
    #     raise InputError('The provided parameter types are invalid.')

    store = data_store.get()

    # Check if the provided email is a valid email address
    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.fullmatch(email_regex, email):
        raise InputError(description='The provided email is not a valid email address.')

    # Check if the provided email is already in use
    for user in store['users']:
        if user['email'] == email and user['removed'] == False:
            raise InputError(description='The provided email is already in use.')

    # Check if password is less than 6 characters
    if len(password) < 6:
        raise InputError(description='The password has to be at least 6 characters.')

    # Check if first name length is within range
    if len(name_first) == 0:
        raise InputError(description='The first name needs to be at least 1 character.')
    if len(name_first) > 50:
        raise InputError(description='Your first name must be within 50 characters.')

    # Check if last name length is within range
    if len(name_last) == 0:
        raise InputError(description='The last name needs to be at least 1 character.')
    if len(name_last) > 50:
        raise InputError(description='Your last name must be within 50 characters.')

    u_id = len(store['users']) + 1

    handle_str = ''.join(char for char in name_first + name_last if char.isalnum())[0:20]
    handle_str_id = -1

    all_handle_str = {user['handle_str'] for user in store['users'] if user['removed'] == False}
    
    while True:
        if handle_str_id == -1:
            if handle_str not in all_handle_str:
                break
        elif f'{handle_str}{handle_str_id}' not in all_handle_str:
            break
        handle_str_id += 1

    if handle_str_id >= 0:
        handle_str = (handle_str + str(handle_str_id))

    global_perm = 2
    if u_id == 1:
        global_perm = 1
    
    # Register user
    user = {
            'user_id': u_id,
            'email': email,
            'password': hashlib.sha256(password.encode()).hexdigest(),
            'name_first': name_first,
            'name_last': name_last,
            'handle_str': handle_str.lower(),
            'global_perm': global_perm,
            'removed': False,
            'sessions': [],
            'reset_codes': [],
            'profile_img_url': f'{url}user/profile/image/default_profile_photo.jpg'
    }

    store['users'].append(user)

    current_unix_time = int(time.time())
    
    # Workspace stats
    if u_id == 1:
        store['workspace_stats'] = {
            "channels_exist": [
                {
                    "num_channels_exist": 0,
                    "time_stamp": current_unix_time
                },
            ],
            "dms_exist": [
                {
                    "num_dms_exist": 0,
                    "time_stamp": current_unix_time
                }
            ],
            "messages_exist": [
                {
                    "num_messages_exist": 0,
                    "time_stamp": current_unix_time
                }
            ]
        }

    # Update user stats
    store['user_stats'][u_id] = {
        'channels_joined': [{'num_channels_joined': 0, 'time_stamp': current_unix_time}],
        'dms_joined': [{'num_dms_joined': 0, 'time_stamp': current_unix_time}],
        'messages_sent': [{'num_messages_sent': 0, 'time_stamp': current_unix_time}], 
        'involvement_rate': 0
    }
    # Notifications
    store['notifications'][u_id] = []

    data_store.set(store)

    token = create_jwt_session_token(user['user_id'])

    return {
        'auth_user_id': u_id,
        'token': token
    }


def auth_logout_v1(auth_user_id, token):
    '''
    This function logouts the user and invalidates its token.

    Arguments:
        auth_user_id    (integer)    - Authenticated User ID
        token           (string)    - Token

    Exceptions:
        InputError
            - Occurs when any of:
                - email entered does not belong to a user
                - password is not correct

    '''
    store = data_store.get()

    for user in store['users']:
        if user['user_id'] == auth_user_id:
            # Check if the provided password is correct
            decoded_token_body = decode_jwt_session_token(token)
            user['sessions'].remove(decoded_token_body['session_id'])
            data_store.set(store)
    
    return {}


def auth_passwordreset_request_v1(email_address):
    '''
    This function sends a password reset code to the user's email upon request.

    Arguments:
        email    (string)    - Email Address

    Return Value:
        Returns {} (dictionary) regardless of conditions
    
    '''
    store = data_store.get()

    # Check if the email is a valid email
    for user in store['users']:
        if user['email'] == email_address:
            
            while True:
                digits = "0123456789"
                reset_code = ""

                for _ in range(6) :
                    reset_code += digits[math.floor(random.random() * 10)]

                # Test whether this generated reset code is already taken
                existing_reset_codes = [reset_code for check_user in store['users'] for reset_code in check_user['reset_codes']]
                if reset_code in existing_reset_codes:
                    continue
                
                # Save reset code
                user['reset_codes'].append(reset_code)
                data_store.set(store)

                # Send Email
                yag = yagmail.SMTP(GMAIL_USERNAME, GMAIL_PASSWORD)
                contents = [f'Password Reset Code: {reset_code}']
                yag.send(user['email'], 'Seams Reset Password', contents)
                break

    return {}


def auth_passwordreset_reset_v1(reset_code, new_password):
    '''
    This function resets the user's password if the reset code is valid.

    Arguments:
        reset_code    (string)    - Reset Code
        new_password  (string)    - New Password

    Exceptions:
        InputError
            - Occurs when any of:
                - reset_code is not a valid reset code
                - password entered is less than 6 characters long
    
    Return Value:
        Returns {} (dictionary) on successful password reset

    '''
    store = data_store.get()

    # Check for password length
    if len(new_password) < 6:
        raise InputError(description='The password has to be at least 6 characters.')

    # Search for reset code
    for user in store['users']:
        if reset_code in user['reset_codes']:
            user['password'] = hashlib.sha256(new_password.encode()).hexdigest()
            user['reset_codes'].remove(reset_code)
            data_store.set(store)
            return {}

    raise InputError(description='The reset code is invalid')
