from src.error import AccessError, InputError
from src.data_store import data_store
from datetime import timezone
from src.helpers import *
import datetime
import uuid
import math
import re
import time

message_send_queue = []


def message_send_v1(user_id, channel_id, message, standup=False):
    '''
    This function sends a message from the specified user to a specified channel
    Arguments:
        user_id (integer)   - User Id number
        channel_id(integer) - Channel Id number
        message(string)     - message string
    Exceptions:
        InputError  - when
            - channel_id does not refer to a valid channel
            - length of message is less than 1 or over 1000 characters
        AccessError - when
            - channel_id is valid and the authorised user is not a member of the channel
    Return Value:
        dictionary of { message_id }
    '''

    if len(message) < 1:
        raise InputError(description="No Message")

    if len(message) > 1000:
        if standup != True:
            raise InputError(description="Message Too Long")

    store = data_store.get()

    loaded_channel = load_channel(store, channel_id)

    if user_id not in loaded_channel['all_members_id']:
        raise AccessError(description="User is not Member")

    message_id = math.trunc(uuid.uuid4().int / math.pow(10,24))
    message_formated = message_format(message_id, user_id, message)

    loaded_channel['messages'].insert(0,message_formated)
    
    # Workspace stats update
    current_unix_time = int(time.time())
    total_msgs = store['workspace_stats']['messages_exist'][-1]['num_messages_exist'] + 1
    store['workspace_stats']['messages_exist'].append({'num_messages_exist': total_msgs, 'time_stamp': current_unix_time})

    # User stats update
    num_msgs = store['user_stats'][user_id]['messages_sent'][-1]['num_messages_sent'] + 1
    store['user_stats'][user_id]['messages_sent'].append({'num_messages_sent': num_msgs, 'time_stamp': current_unix_time})

    # Notifications
    if standup is False:
        tagger = None
        for member in store['users']:
            if member['user_id'] == user_id:
                tagger = member
        for member in store['users']:
            if member['user_id'] in loaded_channel['all_members_id']:
                pattern = f"@{member['handle_str']}([^a-zA-Z0-9:]|$)"
                if re.search(pattern, message):
                    store['notifications'][member['user_id']].append(
                        {'channel_id': channel_id, 'dm_id': -1, 
                        'notification_message': f"{tagger['handle_str']} tagged you in {loaded_channel['name']}: {message[0:20]}"}
                    )

    data_store.set(store)
    return ({
        'message_id' : message_id
    })

def message_edit_v1(user_id, message_id, message):
    '''
    This function edits an already sent message 
    Arguments:
        user_id (integer)   - User Id number
        message_id(integer) - message Id number
        message(string)     - message string
    Exceptions:
        InputError  - when
            - message_id does not refer to a valid message within a channel/DM that the authorised user has joined
            - length of message is over 1000 characters
        AccessError - when both
            - the message was sent by the authorised user making this request
            - the authorised user has owner permissions in the channel/DM
    Return Value:
        dictionary of {}
    '''

    if len(message) > 1000:
        raise InputError(description="Message Too Long")

    store = data_store.get()

    loaded_message = load_message(store, message_id)
    loaded_message_location = load_message_location(store, message_id)
    
    if not is_member(message_id, user_id):
        raise InputError(description="User is not Member")

    if not has_message_perm(message_id, user_id):
        raise AccessError(description="No Permission to edit message")

    if len(message) < 1:
            loaded_message_location['messages'].remove(loaded_message)
    else:
        loaded_message['message'] = message

    data_store.set(store)
    return {}

def message_remove_v1(user_id, message_id):
    '''
    This function deletes a sent message
    Arguments:
        user_id (integer)   - User Id number
        message_id(integer) - message Id number
    Exceptions:
        InputError  - when
            - message_id does not refer to a valid message within a channel/DM that the authorised user has joined
        AccessError - when both
            - the message was sent by the authorised user making this reques
            - the authorised user has owner permissions in the channel/DM
    Return Value:
        dictionary of {}
    '''

    store = data_store.get()

    loaded_message = load_message(store, message_id)
    loaded_message_location = load_message_location(store, message_id)

    if not is_member(message_id, user_id):
        raise InputError(description="User is not Member")

    if not has_message_perm(message_id, user_id):
        raise AccessError(description="No Permission to remove message")

    loaded_message_location['messages'].remove(loaded_message)
    
    # Workspace stats update
    current_unix_time = int(time.time())
    total_msgs = store['workspace_stats']['messages_exist'][-1]['num_messages_exist'] - 1
    store['workspace_stats']['messages_exist'].append({'num_messages_exist': total_msgs, 'time_stamp': current_unix_time})
    
    data_store.set(store)
    return {}

def message_senddm_v1(user_id, dm_id, message):
    '''
    This function sends a message from the specified user to a specified dm
    Arguments:
        user_id (integer)   - User Id number
        dm_id(integer)      - dm Id number
        message(string)     - message string
    Exceptions:
        InputError  - when
            - channel_id does not refer to a valid dm
            - length of message is less than 1 or over 1000 characters
        AccessError - when
            - channel_id is valid and the authorised user is not a member of the dm
    Return Value:
        dictionary of { message_id }
    '''

    if len(message) < 1:
        raise InputError(description="No Message")

    if len(message) > 1000:
        raise InputError(description="Message Too Long")

    store = data_store.get()

    loaded_dm = load_dm(store, dm_id)

    if user_id not in loaded_dm['users']:
        raise AccessError(description="User is not Member")

    message_id = math.trunc(uuid.uuid4().int / math.pow(10,24))
    message_formated = message_format(message_id, user_id, message)

    loaded_dm['messages'].insert(0,message_formated)
    
     # Workspace stats update
    current_unix_time = int(time.time())
    total_msgs = store['workspace_stats']['messages_exist'][-1]['num_messages_exist'] + 1
    store['workspace_stats']['messages_exist'].append({'num_messages_exist': total_msgs, 'time_stamp': current_unix_time})

    # User stats update
    num_msgs = store['user_stats'][user_id]['messages_sent'][-1]['num_messages_sent'] + 1
    store['user_stats'][user_id]['messages_sent'].append({'num_messages_sent': num_msgs, 'time_stamp': current_unix_time})

    # Notifications
    tagger = None
    for member in store['users']:
        if member['user_id'] == user_id:
            tagger = member
    for member in store['users']:
        if member['user_id'] in loaded_dm['users']:
            pattern = f"@{member['handle_str']}([^a-zA-Z0-9:]|$)"
            if re.search(pattern, message):
                store['notifications'][member['user_id']].append(
                    {'channel_id': -1, 'dm_id': dm_id, 
                    'notification_message': f"{tagger['handle_str']} tagged you in {loaded_dm['name']}: {message[0:20]}"}
                )

    data_store.set(store)
    return ({
        'message_id' : message_id
    })

def message_react_v1(user_id, message_id, react_id):
    '''
    This function reacts to a specified message only react_id 1 is set
    Arguments:
        user_id (integer)   - User Id number
        channel_id(integer) - Channel Id number
        react_id(integer)   - reaction
    Exceptions:
        InputError  - when
            - message_id is not a valid message within a channel or DM that the authorised user has joined
            - react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
            - the message already contains a react with ID react_id from the authorised user
        AccessError - when
    Return Value:
        dictionary of { }
    '''
    store = data_store.get()

    loaded_message = load_message(store, message_id)
    react_formated = react_format(react_id, user_id)

    if not is_member(message_id, user_id):
        raise InputError(description="User is not Member")

    for item in loaded_message['reacts']:
        if item == react_formated:
            raise InputError(description="User already reacted")

    loaded_message['reacts'].append(react_formated)

    # Notifications
    reactor = None
    for member in store['users']:
        if member['user_id'] == user_id:
            reactor = member
    found_location_of_message = False
    for channel in store['channels']:
        for message1 in channel['messages']:
            if message1['message_id'] == message_id and loaded_message['u_id'] in channel['all_members_id']:
                found_location_of_message = True
                store['notifications'][loaded_message['u_id']].append(
                    {'channel_id': channel['channel_id'], 'dm_id': -1, 
                    'notification_message': f"{reactor['handle_str']} reacted to your message in {channel['name']}"}
                    )
                break
    if found_location_of_message is False:
        for dm1 in store['dms']:
            for message1 in dm1['messages']:
                if message1['message_id'] == message_id and loaded_message['u_id'] in dm1['users']:
                    store['notifications'][loaded_message['u_id']].append(
                        {'channel_id': -1, 'dm_id': dm1['dm_id'], 
                        'notification_message': f"{reactor['handle_str']} reacted to your message in {dm1['name']}"}
                    )
                    break

    data_store.set(store)

    return {}

def message_unreact_v1(user_id, message_id, react_id):
    '''
    This function unreacts to a specified message only react_id 1 is set
    Arguments:
        user_id (integer)   - User Id number
        channel_id(integer) - Channel Id number
        react_id(integer)   - reaction
    Exceptions:
        InputError  - when
            - message_id is not a valid message within a channel or DM that the authorised user has joined
            - react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
            - the message already contains a react with ID react_id from the authorised user
        AccessError - when
    Return Value:
        dictionary of { }
    '''
    store = data_store.get()

    loaded_message = load_message(store, message_id)
    react_formated = react_format(react_id, user_id)

    if not is_member(message_id, user_id):
        raise InputError(description="User is not Member")

    for item in loaded_message['reacts']:
        if item == react_formated:
            loaded_message['reacts'].remove(react_formated)
            data_store.set(store)
            break
    else:
        raise InputError(description="User hasn't reacted")

    return {}

def message_sendlater_v1 (user_id, channel_id, message, time_sent):
    '''
    This function sends a message from the specified user to a specified channel at the specified time
    Arguments:
        user_id (integer)   - User Id number
        channel_id(integer) - Channel Id number
        message(string)     - message string
        time_sent(integer)  - time to send message
    Exceptions:
        InputError  - when
            - channel_id does not refer to a valid channel
            - length of message is less than 1 or over 1000 characters
            - time_sent is a time in the past
        AccessError - when
            - channel_id is valid and the authorised user is not a member of the channel they are trying to post to
    Return Value:
        dictionary of { message_id }
    '''
    if time_sent < int(time.time()):
        raise InputError(description="time_sent is a time in the past")

    if len(message) < 1:
        raise InputError(description="No Message")

    if len(message) > 1000:
        raise InputError(description="Message Too Long")

    store = data_store.get()

    loaded_channel = load_channel(store, channel_id)

    if user_id not in loaded_channel['all_members_id']:
        raise AccessError(description="User is not Member")

    message_id = math.trunc(uuid.uuid4().int / math.pow(10,24))

    message_send_queue.append({
        'user_id': user_id,
        'location_id' : channel_id,
        'message' : message,
        'time_sent' : time_sent,
        'message_id' : message_id,
        'is_dm' : False,
    })

    return ({
        'message_id' : message_id
    })

def message_sendlaterdm_v1 (user_id, dm_id, message, time_sent):
    '''
    This function sends a message from the specified user to a specified dm at the specified time
    Arguments:
        user_id (integer)   - User Id number
        dm_id(integer)      - DM Id number
        message(string)     - message string
        time_sent(integer)  - time to send message
    Exceptions:
        InputError  - when
            - dm_id does not refer to a valid DM
            - length of message is less than 1 or over 1000 characters
            - time_sent is a time in the past
        AccessError - when
            - dm_id is valid and the authorised user is not a member of the DM they are trying to post to
    Return Value:
        dictionary of { message_id }
    '''
    if time_sent < int(time.time()):
        raise InputError(description="time_sent is a time in the past")

    if len(message) < 1:
        raise InputError(description="No Message")

    if len(message) > 1000:
        raise InputError(description="Message Too Long")

    store = data_store.get()

    loaded_dm = load_dm(store, dm_id)

    if user_id not in loaded_dm['users']:
        raise AccessError(description="User is not Member")

    message_id = math.trunc(uuid.uuid4().int / math.pow(10,24))

    message_send_queue.append({
        'user_id': user_id,
        'location_id' : dm_id,
        'message' : message,
        'time_sent' : time_sent,
        'message_id' : message_id,
        'is_dm': True,
    })

    return ({
        'message_id' : message_id
    })

def message_pin_v1(user_id, message_id):
    '''
    This function Pins a message
    Arguments:
        user_id (integer)   - User Id number
        message_id(integer) - Message Id number
    Exceptions:
        InputError  - when
            - message_id is not a valid message within a channel or DM that the authorised user has joined
            - the message is already pinned
        AccessError - when
            - message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM
    Return Value:
        dictionary of { }
    '''
    store = data_store.get()

    loaded_message = load_message(store, message_id)

    if not is_member(message_id, user_id):
        raise InputError(description="User is not Member")

    if loaded_message['is_pinned'] == True:
        raise InputError(description="Message Already Pinned")

    if not has_channel_perm(message_id, user_id):
        raise AccessError(description="No Permission to Pin Message")

    loaded_message['is_pinned'] = True

    data_store.set(store)
    return{}

def message_unpin_v1(user_id, message_id):
    '''
    This function UnPins a message
    Arguments:
        user_id (integer)   - User Id number
        message_id(integer) - Message Id number
    Exceptions:
        InputError  - when
            - message_id is not a valid message within a channel or DM that the authorised user has joined
            - the message is not already pinned
        AccessError - when
            - message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM
    Return Value:
        dictionary of { }
    '''
    store = data_store.get()

    loaded_message = load_message(store, message_id)

    if not is_member(message_id, user_id):
        raise InputError(description="User is not Member")

    if loaded_message['is_pinned'] == False:
        raise InputError(description="Message Not Pinned")

    if not has_channel_perm(message_id, user_id):
        raise AccessError(description="No Permission to Unpin Message")

    loaded_message['is_pinned'] = False

    data_store.set(store)
    return{}

def message_share_v1(user_id, og_message_id, message, channel_id, dm_id):
    '''
    This function Shares an accesible message to a specified channel or dm the user is in and allows them to add a comment either channel_id or dm_id must be -1 respective to which on isn't being used
    Arguments:
        user_id (integer)       - User Id number
        og_message_id(integer)  - Message Id number
        message(string)         - Message String
        channel_id(integer)     - Channel ID Number
        Dm_id(integer)          - DM ID NUmber
    Exceptions:
        InputError  - when
            - both channel_id and dm_id are invalid
            - neither channel_id nor dm_id are -1
            - og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
            - length of message is more than 1000 characters
        AccessError - when
            - the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised user has not joined the channel or DM they are trying to share the message to
    Return Value:
        dictionary of { shared_message_id }
    '''
    store = data_store.get()

    loaded_message = load_message(store, og_message_id)

    if not is_member(og_message_id, user_id):
        raise InputError(description="User is not Member")

    if len(message) > 1000:
        raise InputError(description="Message Too Long")

    shared_message_id = math.trunc(uuid.uuid4().int / math.pow(10,24))
    message_formated = message_format(shared_message_id, user_id, loaded_message['message'] + "\n'''\n" +message)

    if dm_id == -1:
        loaded_channel = load_channel(store, channel_id)
        if user_id not in loaded_channel['all_members_id']:
            raise AccessError(description= "User not in Channel")

        loaded_channel['messages'].insert(0,message_formated)

    elif channel_id == -1:
        loaded_dm = load_dm(store, dm_id)
        if user_id not in loaded_dm['users']:
            raise AccessError(description= "User not in DM")

        loaded_dm['messages'].insert(0,message_formated)

    else:
        raise InputError(description="neither channel_id or dm_id refer to -1")

    data_store.set(store)
    return {
        'shared_message_id': shared_message_id
    }

# Extra Functions
def message_format(message_id, user_id, message):

    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    message_formated = ({
        'message_id': message_id,
        'u_id': user_id,
        'message': message,
        'time_sent': int(utc_timestamp),
        'reacts' : [],
        'is_pinned' : False,
    })
    
    return message_formated

def react_format(react_id, user_id):

    if react_id != 1:
        raise InputError(description="React ID Doesn't Exsist")

    react_formated = ({
        'react_id' : react_id,
        'u_id' : user_id,
    })

    return react_formated

def message_queue():
    for item in message_send_queue:
        if item['time_sent'] <= int(time.time()):
            send_message_forced_id(item['message_id'], item['user_id'], item['location_id'], item['message'], item['is_dm'])
            message_send_queue.remove(item)

def send_message_forced_id(message_id, user_id, location_id, message, is_dm):

    store = data_store.get()

    if is_dm == False:
        loaded = load_channel(store, location_id)
    else:
        loaded = load_dm(store, location_id)

    message_formated = message_format(message_id, user_id, message)


    # Workspace stats update
    current_unix_time = int(time.time())
    total_msgs = store['workspace_stats']['messages_exist'][-1]['num_messages_exist'] + 1
    store['workspace_stats']['messages_exist'].append({'num_messages_exist': total_msgs, 'time_stamp': current_unix_time})

    # User stats update
    num_msgs = store['user_stats'][user_id]['messages_sent'][-1]['num_messages_sent'] + 1
    store['user_stats'][user_id]['messages_sent'].append({'num_messages_sent': num_msgs, 'time_stamp': current_unix_time})

    # Notifications
    tagger = None
    for member in store['users']:
        if member['user_id'] == user_id:
            tagger = member
    if is_dm:
        for member in store['users']:
            if member['user_id'] in loaded['users']:
                pattern = f"@{member['handle_str']}([^a-zA-Z0-9:]|$)"
                if re.search(pattern, message):
                    store['notifications'][member['user_id']].append(
                        {'channel_id': -1, 'dm_id': loaded['dm_id'], 
                        'notification_message': f"{tagger['handle_str']} tagged you in {loaded['name']}: {message[0:20]}"}
                    )
    else:
        for member in store['users']:
            if member['user_id'] in loaded['all_members_id']:
                pattern = f"@{member['handle_str']}([^a-zA-Z0-9:]|$)"
                if re.search(pattern, message):
                    store['notifications'][member['user_id']].append(
                        {'channel_id': loaded['channel_id'], 'dm_id': -1, 
                        'notification_message': f"{tagger['handle_str']} tagged you in {loaded['name']}: {message[0:20]}"}
                    )

    loaded['messages'].insert(0,message_formated)
    data_store.set(store)

def is_member(message_id, u_id):
    store = data_store.get()
    for channel in store['channels']:
        if u_id in channel['all_members_id']:
            for message in channel['messages']:
                if message['message_id'] == message_id:
                    return True
    for dm in store['dms']:
        if u_id in dm['users']:
            for message in dm['messages']:
                if message['message_id'] == message_id:
                    return True
    return False

def has_message_perm(message_id, u_id):

    store = data_store.get()

    loaded_message = load_message(store, message_id)
    loaded_user = load_user(store, u_id)
    loaded_dm = None
    loaded_channel = None

    for channel in store['channels']:
        if u_id in channel['all_members_id']:
            for item in channel['messages']:
                if message_id == item['message_id']:
                    loaded_channel = channel
    
    for dm in store['dms']:
        if u_id in dm['users']:
            for item in dm['messages']:
                if message_id == item['message_id']:
                    loaded_dm = dm

    if loaded_channel != None:
        if u_id != loaded_message['u_id'] and u_id not in loaded_channel['owner_members_id'] and loaded_user['global_perm'] == 2:
            return False

    if loaded_dm != None:
        if u_id != loaded_message['u_id'] and u_id != loaded_dm['owner']:
            return False

    return True

def has_channel_perm(message_id, u_id):
    store = data_store.get()

    loaded_user = load_user(store, u_id)
    loaded_dm = None
    loaded_channel = None

    for channel in store['channels']:
        if u_id in channel['all_members_id']:
            for item in channel['messages']:
                if message_id == item['message_id']:
                    loaded_channel = channel
    
    for dm in store['dms']:
        if u_id in dm['users']:
            for item in dm['messages']:
                if message_id == item['message_id']:
                    loaded_dm = dm

    if loaded_channel != None:
        if u_id not in loaded_channel['owner_members_id'] and loaded_user['global_perm'] == 2:
            print(loaded_channel['owner_members_id'])
            return False

    if loaded_dm != None:
        if u_id != loaded_dm['owner']:
            return False

    return True