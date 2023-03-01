import jwt
import uuid

from src.data_store import data_store
from src.error import *

SECRET = "AVerySecretSecret"

# Returns token
def create_jwt_session_token(user_id):
    store = data_store.get()

    created_token = None
    for user in store['users']:
        if user['user_id'] == user_id:
            session_id = str(uuid.uuid4())

            token = jwt.encode({
                'user_id': user['user_id'],
                'session_id': session_id
            }, SECRET, algorithm='HS256')

            user['sessions'].append(session_id)
            data_store.set(store)
            created_token = token

    return created_token

    

# returns auth_user_id
def verify_jwt_session_token(token):
    decoded_body = decode_jwt_session_token(token)

    if decoded_body is None:
        return None

    store = data_store.get()

    for searched_user in store['users']:
        if searched_user['user_id'] == decoded_body['user_id'] and decoded_body['session_id'] in searched_user['sessions']:
            return searched_user['user_id']

    return None

# returns decoded token body
def decode_jwt_session_token(token):
    try:
        return jwt.decode(token, SECRET, algorithms=['HS256'])
    except Exception:
        return None


def get_full_user_object(user_id):
    store = data_store.get()

    searched_user = None
    for user in store['users']:
        if user['user_id'] == user_id:
            searched_user = user
    
    return searched_user


def get_user_output(user_id):
    store = data_store.get()

    searched_user = {}
    for user in store['users']:
        if user['user_id'] == user_id:
            searched_user['u_id'] = user['user_id']
            searched_user['email'] = user['email']
            searched_user['name_first'] = user['name_first']
            searched_user['name_last'] = user['name_last']
            searched_user['handle_str'] = user['handle_str']
            searched_user['profile_img_url'] = user['profile_img_url']

    return searched_user

def load_dm(store, dm_id):

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            loaded_dm = dm
            break
    else:
        raise InputError(description="Dm ID Doesn't Exsist")
    
    return loaded_dm 

def load_channel(store, channel_id):

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            loaded_channel = channel
            break
    else:
        raise InputError(description="Channel ID Doesn't Exsist")

    return loaded_channel

def load_message(store, message_id):

    loaded_message = None

    for dm in store['dms']:
        for message in dm['messages']:
            if message['message_id'] == message_id:
                loaded_message = message

    for channel in store['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                loaded_message = message
    
    if loaded_message == None :
        raise InputError(description="Message Id Invalid")

    return loaded_message

def load_message_location(store, message_id):

    output = None
    
    for dm in store['dms']:
        for message in dm['messages']:
            if message['message_id'] == message_id:
                output = dm

    for channel in store['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                output = channel

    return output

def load_user(store, u_id):

    output = None
    
    for user in store['users']:
        if user['user_id'] == u_id:
            output = user
    return output

def is_reacted(u_id, message, react_id):
    
    for react in message['reacts']:
        if react['react_id'] == react_id and react['u_id'] == u_id:
            return True
    return False