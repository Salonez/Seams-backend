from src.error import InputError, AccessError
from src.data_store import data_store
import time

def channels_list_v1(auth_user_id):
    '''
    This function lists all channels the authorised user is a part of
    Arguments:
        auth_user_id (integer)    - User Id number
    Exceptions:
        AccessError - when
            - auth_user_id does not exist
    Return Value:
        dictionary of {'channel id number', 'name of the channel'}
    '''

    store = data_store.get()
    channel_list = []

    for channel in store["channels"]:
        for user in channel['all_members_id']:
            if user == auth_user_id:
                channel_list.append({
                    'channel_id': channel['channel_id'],
                    'name': channel['name'],
                })
                
    return {
        'channels': channel_list,
    }

def channels_listall_v1(auth_user_id):
    '''
    This function lists all channels both private and public in the data store
    Arguments:
        auth_user_id (integer)    - User Id number
    Exceptions:
        AccessError - when
            - auth_user_id does not exist
    Return Value:
        dictionary of {'channel id number', 'name of the channel'}
    '''

    store = data_store.get()
    channel_list = []
    
    for channel in store["channels"]:
        channel_list.append({
            'channel_id': channel['channel_id'],
            'name': channel['name'],
        })
    return {
        'channels': channel_list,
    }

def channels_create_v1(auth_user_id, name, is_public):
    '''
    Creates a new channel with the name given. This user is then added to the channel.
    Arguments:
        auth_user_id (integer)    - User Id number
        is_public (boolean) - Shows if the channel is public or private
    Exceptions:
        AccessError - when auth_user_id does not exist
        InputError  - when naming errors occur, under one character or more than 20
    Return Value:
        dictionary of {'channel id number'}
    '''
    data = data_store.get()

    # raise InputError for naming errors.
    if len(name) > 20 or len(name) < 1:
        raise InputError(description="name error")

    auth_user = [user for user in data['users'] if user['user_id'] == auth_user_id][0]

    #find channel id here 

    channel_id = len(data['channels']) + 1

    new_channel = {
        'channel_id': channel_id,
        'name' : name,
        'is_public' : is_public,
        'owner_members_id' : [auth_user['user_id']],
        'all_members_id' : [auth_user['user_id']],
        'messages' : [],
    }

    data['channels'].append (new_channel)

    # Update workspace stats
    current_unix_time = int(time.time())
    total_channels = data['workspace_stats']['channels_exist'][-1]['num_channels_exist'] + 1
    data['workspace_stats']['channels_exist'].append({'num_channels_exist': total_channels, 'time_stamp': current_unix_time})

    # Update user stats
    num_channels = data['user_stats'][auth_user_id]['channels_joined'][-1]['num_channels_joined'] + 1
    data['user_stats'][auth_user_id]['channels_joined'].append({'num_channels_joined': num_channels, 'time_stamp': current_unix_time})

    data_store.set(data)

    return {
        'channel_id': channel_id,
    }
