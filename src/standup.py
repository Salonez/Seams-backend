import datetime
from threading import Timer
from src.error import InputError, AccessError
from src.data_store import data_store
from src.message import message_send_v1

def send_standup_to_channel(auth_user_id, channel_id):
    """
    helper function which sends the standup with all sent messages 
    to the channel after the wait time is completed
    """
    store = data_store.get()

    messages = ''
    for standup in store['standups']:
        if standup['channel_id'] == channel_id:
            messages = "\n".join(standup['messages'])
            message_send_v1(auth_user_id, channel_id, messages, standup=True)
            store = data_store.get()
            store['standups'].remove(standup)
            data_store.set(store)

        


def standup_start_v1(auth_user_id, channel_id, length):
    """
    This function starts a standup for the set amount of time which within if 
    someone sends a message to the standup, it is buffered. Once the standup is over, 
    the messages are sent to the channel
    Arguments:
        auth_user_id (integer)    - User Id number
        channel_id (integer)      - Channel id number
        lenght (integer)          - length of standup 

    Exceptions:
        AccessError - when
            - auth_user_id is valid but not member of channel_id
            - auht_user_id is not valid
        InputError - when
            - channel_id is not valid
            - length is negative integer
            - standup is already actiely running

    Return Value:
        dictionary of {'time_finish'}
    """

    store = data_store.get()

    #check if id is valid
    if auth_user_id not in [users['user_id'] for users in store['users']]:
        raise AccessError(description='user id is not valid')

    #chack valid channel id
    if channel_id not in [channels['channel_id'] for channels in store['channels']]:
        raise InputError(description='channel id is not valid')

    #check length is positive
    if length < 0:
        raise InputError(description='length of standup must be positive number')
    
    #check no standup is currently active in channel
    if channel_id in [standups['channel_id'] for standups in store['standups']]:
        raise InputError(description='standup is currently active in the channel')

    #check user is in channel
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            if auth_user_id not in channels['all_members_id']:
                raise AccessError(description='user does not have access to this channel')


    time_add = datetime.datetime.now() + datetime.timedelta(seconds=length)
    time_finish = time_add.timestamp()

    add_standup = {
        'auth_user_id': auth_user_id,
        'channel_id': channel_id,
        'time_finish': time_finish,
        'messages': []
    }

    store['standups'].append(add_standup)
    data_store.set(store)

    start_time = Timer(length, send_standup_to_channel, 
                args=(add_standup['auth_user_id'], add_standup['channel_id']))
    start_time.start()

    return {'time_finish': time_finish}

def standup_active_v1(auth_user_id, channel_id):
    """
    This function returns whether there is currently an active standup running the channel
    and also when the standup finishes
    Arguments:
        auth_user_id (integer)      - User Id number
        channel_id (integer)        - Channel Id number

    Exceptions:
        AccessEror:
            - auth_user_id is valid but not a member of channel_id
            - auht_user_id is not valid
        InputError:
            - channel_id is not valid
    
    Return Value:
        dictionary of {'is_active', 'time_finish'}
    """

    store = data_store.get()

    #check if id is valid
    if auth_user_id not in [users['user_id'] for users in store['users']]:
        raise AccessError(description='user id is not valid')

    #chack valid channel id
    if channel_id not in [channels['channel_id'] for channels in store['channels']]:
        raise InputError(description='channel id is not valid')

    #check user is in channel
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            if auth_user_id not in channels['all_members_id']:
                raise AccessError(description='user does not have access to this channel')

    is_active = False
    time_finish = None

    for standup in store['standups']:
        if standup['channel_id'] == channel_id:
            time_finish = standup['time_finish']
            is_active = True


    return {
        'is_active': is_active,
        'time_finish': time_finish
    }

def standup_send_v1(auth_user_id, channel_id, message):
    """
    this function acepts messages sent to be buffered in standup queue
    Arguments:
        auth_user_id (integer)      - User Id number
        channel_id (integer)        - Channel Id number
        message (string)            - message to be buffered
    
    Exceptions:
        AccessError:
            - auth_user_id is valid but not a member of channel_id
            - auth_user_id is not valid
        InputError:
            - channel_id is not valid
            - length of message is over 1000 characters
            - there is not a current active standup in channel

    Return Value:
        dictionary of {}
        
    """
    store = data_store.get()

    #check if id is valid
    if auth_user_id not in [users['user_id'] for users in store['users']]:
        raise AccessError(description='user id is not valid')

    #chack valid channel id
    if channel_id not in [channels['channel_id'] for channels in store['channels']]:
        raise InputError(description='channel id is not valid')

    #check length is positive
    if len(message) > 1000:
        raise InputError(description='message must be less than 1000 characters')
    
    #check no standup is currently active in channel
    if channel_id not in [standups['channel_id'] for standups in store['standups']]:
        raise InputError(description='standup is currently active in the channel')

    #check user is in channel
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            if auth_user_id not in channels['all_members_id']:
                raise AccessError(description='user does not have access to this channel')
    
    handle_user = ''
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            handle_user = user['handle_str']
    message_add = handle_user + ': ' + message
    str(message_add)
    for standup in store['standups']:
        if standup['channel_id'] == channel_id:
            standup['messages'].append(message_add)

    data_store.set(store)
    return {}