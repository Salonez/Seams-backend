'''Channel Functions'''
import time
from src.error import AccessError, InputError
from src.data_store import data_store
import jwt
from src.helpers import get_user_output, is_reacted

def channel_leave_v1(auth_user_id, channel_id):
    '''
    Given a channel with ID channel_id that the authorised user is a member of, 
    remove them as a member of the channel. Their messages should remain in 
    the channel. If the only channel owner leaves, the channel will remain.

    Arguments:
        auth_user_id    (integer)    - user id of the user leaving.
        channel_id      (integer)    - Channel id of the channel the user is leaving.

    Exceptions:
        InputError
            - when channel_id does not refer to a valid channel
        AccessError
            - when:
                - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns None
    '''
    # Error checks
    if is_channel(channel_id) is False:
        raise InputError(description='channel_id does not refer to a valid channel')
    if check_if_member(auth_user_id, channel_id) is False:
        raise AccessError(description='user is not a member of the channel')

    # Removing user from channel
    store = data_store.get()
    loaded_channel = None
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            loaded_channel = channel
    loaded_channel['all_members_id'].remove(auth_user_id)
    # Check if owner
    if check_if_owner(auth_user_id, channel_id) is True:
        loaded_channel['owner_members_id'].remove(auth_user_id)
    
    # User stats update
    current_unix_time = int(time.time())
    num_channels = store['user_stats'][auth_user_id]['channels_joined'][-1]['num_channels_joined'] - 1
    store['user_stats'][auth_user_id]['channels_joined'].append({'num_channels_joined': num_channels, 'time_stamp': current_unix_time})
        
    data_store.set(store)

    return {
    }

    

def channel_invite_v1(auth_user_id, channel_id, u_id):

    '''
    This function invites a user with ID u_id to join a channel with ID channel_id.
    The user is immediately added.

    Arguments:
        auth_user_id    (integer)    - user id of the user inviting.
        u_id            (integer)    - user id of the user being invited.
        channel_id      (integer)    - Channel id for the user to be added to.

    Exceptions:
        InputError
            - when any of:
                - channel_id does not refer to a valid channel
                - u_id does not refer to a valid user
                - u_id refers to a user who is already a member of the channel
        AccessError
            - when:
                - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns None
    '''

    store = data_store.get()

    # Check that u_id is a valid id.
    check_u = False
    for user in store['users']:
        if user['user_id'] == u_id:
            check_u = True
            break
    if check_u is False:
        raise InputError(description='u_id does not refer to a valid user')

    # Find channel in store, then check that auth_user is a member and
    # that user is not a member. If both conditions hold, add user to channel.
    check_channel = False
    loaded_channel = None
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            check_channel = True
            if auth_user_id not in channel['all_members_id']:
                raise AccessError(description='Authorised user is not a member of the channel')
            if u_id in channel['all_members_id']:
                raise InputError(description='user already a member of the channel')
            # Adding user to channel
            channel['all_members_id'].append(u_id)
            loaded_channel = channel
            break
    # Check if channel was not found.
    if check_channel is False:
        raise InputError(description='channel_id does not refer to a valid channel')

    # Update user stats
    current_unix_time = int(time.time())
    num_channels = store['user_stats'][u_id]['channels_joined'][-1]['num_channels_joined'] + 1
    store['user_stats'][u_id]['channels_joined'].append({'num_channels_joined': num_channels, 'time_stamp': current_unix_time})
    # Notifications
    channel_user = None
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            channel_user = user
    store['notifications'][u_id].append(
        {'channel_id': channel_id, 'dm_id': -1, 
        'notification_message': f"{channel_user['handle_str']} added you to {loaded_channel['name']}"}
    )

    # Save data
    data_store.set(store)

    return {
    }

def channel_details_v1(auth_user_id, channel_id):

    '''
    This function given a channel_id, provides basic details about the channel, provided that
    the authorised user is a member it.

    Arguments:
        auth_user_id    (integer)    - user id of person trying to access basic details
                                       of specified channel.
        channel_id      (integer)    - Channel id of wanted channel.

    Exceptions:
        InputError
            - when:
                - channel_id does not refer to a valid channel
        AccessError
            - when:
                - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        {'name of channel', 'if channel is public', 'details on channel owners',
        'details on channel members'}

    '''

    store = data_store.get()

    # Find ids of wanted information stored in store['channels'].
    searched_channel = None
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            searched_channel = channel
            break

    # Check valid channel_id and if user is authorised.
    if searched_channel is None:
        raise InputError(description="Invalid channel")
    if auth_user_id not in searched_channel['all_members_id']:
        raise AccessError(description="Unauthorised access")
    # owner_members = [get_user_output(member_id) for member_id in searched_channel['owner_members_id']]
    # all_members = [get_user_output(member_id) for member_id in searched_channel['all_members_id']]

    owner_members = []
    all_members = []
    # Find full information on owners and members.
    for user_details in store['users']:
        for member_id in searched_channel['all_members_id']:
            if member_id == user_details['user_id']:
                all_members.append({
                    'u_id': user_details['user_id'],
                    'email': user_details['email'],
                    'name_first': user_details['name_first'],
                    'name_last': user_details['name_last'],
                    'handle_str': user_details['handle_str'],
                    'profile_img_url' : user_details['profile_img_url'],
                })
                if member_id in searched_channel['owner_members_id']:
                    owner_members.append({
                        'u_id': user_details['user_id'],
                        'email': user_details['email'],
                        'name_first': user_details['name_first'],
                        'name_last': user_details['name_last'],
                        'handle_str': user_details['handle_str'],
                        'profile_img_url' : user_details['profile_img_url'],
                    })

    return {
            'name': searched_channel['name'],
            'is_public': searched_channel['is_public'],
            'owner_members': owner_members,
            'all_members': all_members,
            }

def channel_addowner_v1(auth_user_id, channel_id, u_id):
    '''
    This function makes user with user id u_id an owner of the channel.

    Arguments:
        auth_user_id    (integer)    - user id of the user adding owner.
        u_id            (integer)    - user id of the user to be added as an owner.
        channel_id      (integer)    - Channel id for the channel user will become owner of.

    Exceptions:
        InputError
            - when any of:
                - channel_id does not refer to a valid channel
                - u_id does not refer to a valid user
                - u_id refers to a user who is not a member of the channel
                - u_id refers to a user who is already an owner of the channel
        AccessError
            - when:
                - channel_id is valid and the authorised user is not an owner of the channel

    Return Value:
        Returns None
    '''
    

    # Error checks

    if not is_channel(channel_id):
        raise InputError(description="Incorrect Channel ID")
    if not check_if_owner(auth_user_id, channel_id):
        if have_global_perm(auth_user_id) != 1:
            raise AccessError(description="Auth does not have permission to add owner")
        elif not check_if_member(auth_user_id, channel_id):
            raise AccessError(description="Auth does not have permission to add owner")
    if not is_user(u_id):
        raise InputError(description="User Doesnt Exist")
    if not check_if_member(u_id, channel_id):
        raise InputError(description="User not member of channel")
    if check_if_owner(u_id, channel_id):
        raise InputError(description="User already an owner")

    # Making user an owner
    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel['owner_members_id'].append(u_id)
    data_store.set(store)

    return {
    }

def channel_removeowner_v1(auth_user_id, channel_id, u_id):
    '''
    Remove user with user id u_id as an owner of the channel.

    Arguments:
        auth_user_id    (integer)    - user id of the user removing owner.
        u_id            (integer)    - user id of the user to be removed from being an owner.
        channel_id      (integer)    - Channel id for the channel user the ownership removal will be from.

    Exceptions:
        InputError
            - when any of:
                - channel_id does not refer to a valid channel
                - u_id does not refer to a valid user
                - u_id refers to a user who is not an owner of the channel
                - u_id refers to a user who is currently the only owner of the channel
        AccessError
            - when:
                - channel_id is valid and the authorised user is not an owner of the channel

    Return Value:
        Returns None
    '''
    # Error checks
    if not is_channel(channel_id):
        raise InputError(description="Incorrect Channel ID")
    if not check_if_owner(auth_user_id, channel_id):
        if have_global_perm(auth_user_id) != 1:
            raise AccessError(description="Auth does not have permission to add owner")
        elif not check_if_member(auth_user_id, channel_id):
            raise AccessError(description="Auth does not have permission to add owner")
    if not is_user(u_id):
        raise InputError(description="User Doesnt Exist")
    if not check_if_owner(u_id, channel_id):
        raise InputError(description="User not owner of channel")
    # Check user is not the only owner
    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            if len(channel['owner_members_id']) == 1:
                raise InputError(description="User is currently the only owner of the channel")
    
    # Remove owner
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel['owner_members_id'].remove(u_id)
    data_store.set(store)

    return {
    }
    

def channel_messages_v1(auth_user_id, channel_id, start):
    '''
    Returns last 50 messages from start

    Arguments:
        auth_user_id (integer)    - User Identification Number
        channel_id (integer)    - Channel Identification Number
        start (integer)     - Starting Message
    ...

    Exceptions:
        InputError  - Occurs when
            - Incorrect channel ID
            - Start is out of range / Larger than total messages
        AccessError - Occurs when
            - Not a member in the channel attempting to access messages from

    Return Value:
        returns dictionary - {[messages], start, end}
    '''
    store = data_store.get()

    # User Check
    # if not is_user(auth_user_id):
    #     raise AccessError("User Doesnt Exist")

    if not is_channel(channel_id):
        raise InputError(description="Incorrect Channel ID")

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            loaded_channel = channel

    if auth_user_id not in loaded_channel['all_members_id']:
        raise AccessError(description="Not A Member In Channel")

    if len(loaded_channel['messages']) < start:
        raise InputError(description="Start Larger Then Total Messages")

    message_list = []
    for message in loaded_channel['messages'][start:start+50]:
        message_list.append({
            'message_id': message['message_id'],
            'u_id': message['u_id'],
            'message': message['message'],
            'time_sent': message['time_sent'],
            'reacts' : [{
                'react_id' : 1,
                'u_ids' : [ item['u_id'] for item in message['reacts'] ],
                'is_this_user_reacted' : is_reacted(auth_user_id, message, 1)
            }],
            'is_pinned' : message['is_pinned'],
        })
        
    if len(message_list) == 50:

        data_store.set(store)

        return {
            'messages': message_list,
            'start': start,
            'end': start + 50,
        }

    data_store.set(store)

    return {
        'messages': message_list,
        'start': start,
        'end': -1,
    }

def channel_join_v1(auth_user_id, channel_id):
    '''
    Adds authorized user to a channel

    Arguments:
        auth_user_id (integer)    - User Identification Number
        channel_id (integer)    - Channel Identification Number
    ...

    Exceptions:
        InputError  - Occurs when
            - Incorrect channel ID
            - User already in channel
        AccessError - Occurs when
            - User joining private channel without owner permissions

    Return Value:
    '''
    store = data_store.get()

    # Channel ID Check
    if not is_channel(channel_id):
        raise InputError(description="Incorrect Channel ID")

    # Load Channel
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            loaded_channel = channel

    #Already in Channel
    if auth_user_id in loaded_channel['all_members_id']:
        raise InputError(description="Already Joined Channel")

    #Public Channel
    if loaded_channel['is_public']:
        loaded_channel['all_members_id'].append(auth_user_id)
        # Update user stats
        current_unix_time = int(time.time())
        num_channels = store['user_stats'][auth_user_id]['channels_joined'][-1]['num_channels_joined'] + 1
        store['user_stats'][auth_user_id]['channels_joined'].append({'num_channels_joined': num_channels, 'time_stamp': current_unix_time})
        data_store.set(store)
        return {}

    loaded_user = None
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            loaded_user = user

    print("global id is")
    print(loaded_user['global_perm'])


    #Private Channel
    for user in loaded_channel['owner_members_id']:
        if user == auth_user_id or loaded_user['global_perm'] == 1:
            loaded_channel['all_members_id'].append(auth_user_id)
            # Update user stats
            current_unix_time = int(time.time())
            num_channels = store['user_stats'][auth_user_id]['channels_joined'][-1]['num_channels_joined'] + 1
            store['user_stats'][auth_user_id]['channels_joined'].append({'num_channels_joined': num_channels, 'time_stamp': current_unix_time})
            data_store.set(store)
            return {}
    raise AccessError(description="No Permission to Join")

def is_channel(channel_id):
    '''
    Checks if Channel Exists

    Arguments:
        channel_id (integer)    - Channel Identification Number
    ...

    Exceptions:

    Return Value:
        Boolean
    '''
    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            return True
    return False

def is_user(user_id):
    '''
    Checks if User Exists

    Arguments:
        user_id (integer)    - User Identification Number
    ...

    Exceptions:

    Return Value:
        Boolean
    '''
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == user_id:
            return True
    return False

def check_if_member(u_id, channel_id):
    '''
    Checks if user is in channel

    Arguments:
        u_id (integer)      - User Identification Number
        channel_id(integer) - channel identification number

    Exceptions:

    Return Value:
        Boolean
    '''
    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            if u_id in channel['all_members_id']:
                return True
    return False
def check_if_owner(u_id, channel_id):
    '''
    Checks if user is owner of channel

    Arguments:
        u_id (integer)      - User Identification Number
        channel_id(integer) - channel identification number

    Exceptions:

    Return Value:
        Boolean
    '''
    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            if u_id in channel['owner_members_id']:
                return True
    return False

def have_global_perm(user_id):
    '''
    Checks if User has global permissions

    Arguments:
        user_id (integer)    - User Identification Number
    ...

    Exceptions:

    Return Value:
        Boolean
    '''
    store = data_store.get()
    global_perm = None
    for user in store['users']:
        if user['user_id'] == user_id:
            global_perm = user['global_perm']
    return global_perm

