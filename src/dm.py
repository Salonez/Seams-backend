from src.error import AccessError, InputError
from src.data_store import data_store
import time
from src.helpers import get_user_output, is_reacted

def dm_create_v1(auth_user_id, u_ids):
    '''
    Creates a Dm with owner auth_user and members u_ids
    Arguments:
        auth_user_id (integer)    - User Id number (Owner)
        u_ids list - list of ids other than the owner in dm
    Exceptions:
        InputError  - any u_id in u_ids does not refer to a valid user
                    - there are duplicate 'u_id's in u_ids
    Return Value:
        {'dm_id' : dm_id}
    '''
    data = data_store.get()
    dm_id = len(data['dms']) + 1
 
    if len(u_ids) != len(set(u_ids)):
        raise InputError(description="duplicate u_id in u_ids")
        
    u_ids.insert(0,auth_user_id)
    names_list = []
    
    for user_id in u_ids:
        for user in data['users']:
            if user['user_id'] == user_id:
                names_list.append(user['handle_str'])
                break
        else:
            raise InputError(description="u_ids does not refer to valid user")

    names_list.sort()
    str_of_names = ", ".join(names_list)
    
    new_dm = {
        'dm_id' : dm_id,
        'name' : str_of_names,
        'owner' : auth_user_id,
        'users' : u_ids,
        'messages' : [],
    }

    data['dms'].append(new_dm)

    # Update workspace stats
    current_unix_time = int(time.time())
    total_dms = data['workspace_stats']['dms_exist'][-1]['num_dms_exist'] + 1
    data['workspace_stats']['dms_exist'].append({'num_dms_exist': total_dms, 'time_stamp': current_unix_time})

    # Update user stats
    num_dms = data['user_stats'][auth_user_id]['dms_joined'][-1]['num_dms_joined'] + 1
    data['user_stats'][auth_user_id]['dms_joined'].append({'num_dms_joined': num_dms, 'time_stamp': current_unix_time})
    for u_id in u_ids:
        if u_id != auth_user_id:
            num_dms = data['user_stats'][u_id]['dms_joined'][-1]['num_dms_joined'] + 1
            data['user_stats'][u_id]['dms_joined'].append({'num_dms_joined': num_dms, 'time_stamp': current_unix_time})
    # Notifications
    dm_creator = None
    for user in data['users']:
        if user['user_id'] == auth_user_id:
            dm_creator = user
    for u_id in u_ids:
        if u_id != auth_user_id:
            data['notifications'][u_id].append(
                {'channel_id': -1, 'dm_id': dm_id,
                'notification_message': f"{dm_creator['handle_str']} added you to {str_of_names}"}
            )

    data_store.set(data)

    return {
        'dm_id': dm_id,
    }

def dm_list_v1(auth_user_id):
    '''
    lists all dms user is in
    Arguments:
        auth_user_id (integer)    - User Id number
    Exceptions:
        None
    Return Value:
        {'dms' : [{'dm_id': dm_id,'name': name}]}
    '''
    data = data_store.get()
    dms = []

    for dm in data["dms"]:
        for user in dm['users']:
            if user == auth_user_id:
                dms.append({
                    'dm_id': dm['dm_id'],
                    'name': dm['name'],
                })
                
    return {
        'dms': dms
    }
    

def dm_remove_v1(auth_user_id, given_dm_id):
    '''
    removes dm given valid auth user and dm
    Arguments:
        auth_user_id (integer)  - User Id number (owner)
        given_dm_id (integer)   - Dm Id number
    Exceptions:
        Input Error 
            - dm_id does not refer to a valid DM
        Access Error
            - dm_id is valid and the authorised user is not the original DM creator
            - dm_id is valid and the authorised user is no longer in the DM
    Return Value:
        {}
    '''
    data = data_store.get()

    found_dm = [dm for dm in data['dms'] if dm['dm_id'] == given_dm_id]

    # dm_id does not exist
    if found_dm == []: 
        raise InputError(description="dm_id does not refer to valid dm")

    found_dm = found_dm[0]
    
    # Check permission of auth_user_id
    if auth_user_id != found_dm['owner']:
        raise AccessError(description="user is not original dm creator")

    # Check person is member of dm 
    if auth_user_id not in found_dm['users']:
        raise AccessError(description="user no longer in channel")

    
    # Workspace stats update
    current_unix_time = int(time.time())
    total_dms = data['workspace_stats']['dms_exist'][-1]['num_dms_exist'] - 1
    data['workspace_stats']['dms_exist'].append({'num_dms_exist': total_dms, 'time_stamp': current_unix_time})
    total_msgs = data['workspace_stats']['messages_exist'][-1]['num_messages_exist'] - len(found_dm['messages'])
    data['workspace_stats']['messages_exist'].append({'num_messages_exist': total_msgs, 'time_stamp': current_unix_time})

    
    # Remove dm
    data['dms'].remove(found_dm)

    # Update user stats
    num_dms = data['user_stats'][auth_user_id]['dms_joined'][-1]['num_dms_joined'] - 1
    data['user_stats'][auth_user_id]['dms_joined'].append({'num_dms_joined': num_dms, 'time_stamp': current_unix_time})
    for u_id in found_dm['users']:
        if u_id != auth_user_id:
            num_dms = data['user_stats'][u_id]['dms_joined'][-1]['num_dms_joined'] - 1
            data['user_stats'][u_id]['dms_joined'].append({'num_dms_joined': num_dms, 'time_stamp': current_unix_time})

    data_store.set(data)
                
    return {}

def dm_details_v1(auth_user_id, given_dm_id):
    '''
    Given valid user and dm returns dm details
    Arguments:
        auth_user_id (integer)  - User Id number (owner)
        given_dm_id (integer)   - Dm Id number
    Exceptions:
        Input Error 
            - dm_id does not refer to a valid DM
        Access Error
            - dm_id is valid and the authorised user is not a member of the DM
    Return Value:
        { 'name' : name, 'members' : [user] }
    '''
    data = data_store.get()

    found_dm = [dm for dm in data['dms'] if dm['dm_id'] == given_dm_id]

    # dm_id does not exist
    if len(found_dm) == 0: 
        raise InputError(description="dm_id does not refer to valid dm")

    found_dm = found_dm[0]

    # Check person is member of dm 
    if auth_user_id not in found_dm['users']:
        raise AccessError(description="user not in dm")

    members = []
    # for user in data['users'] :
    #     for id in found_dm['users']:
    #         if user['user_id'] == id:
    #             members.append({
    #                 'u_id' :  user['user_id'],
    #                 'email' : user['email'],
    #                 'name_first' : user['name_first'],
    #                 'name_last' : user['name_last'],
    #                 'handle_str' : user['handle_str'],
    #             })
    members = [get_user_output(id) for id in found_dm['users']]

    return {
        'name' : found_dm['name'],
        'members' : members,
    }
    
def dm_leave_v1(auth_user_id, given_dm_id):
    '''
    Given valid user and dm leaves the dm dm still exists if owner leaves
    Arguments:
        auth_user_id (integer)  - User Id number (owner)
        given_dm_id (integer)   - Dm Id number
    Exceptions:
        Input Error 
            - dm_id does not refer to a valid DM
        Access Error
            - dm_id is valid and the authorised user is not a member of the DM
    Return Value:
        {}
    '''
    data = data_store.get()

    found_dm = [dm for dm in data['dms'] if dm['dm_id'] == given_dm_id]

    # dm_id does not exist
    if len(found_dm) == 0: 
        raise InputError(description="dm_id does not refer to valid dm")

    found_dm = found_dm[0]

    # Check person is member of dm 
    if auth_user_id not in found_dm['users']:
        raise AccessError(description="user not in dm")

    found_dm['users'].remove(auth_user_id)

    # Update user stats
    current_unix_time = int(time.time())
    num_dms = data['user_stats'][auth_user_id]['dms_joined'][-1]['num_dms_joined'] - 1
    data['user_stats'][auth_user_id]['dms_joined'].append({'num_dms_joined': num_dms, 'time_stamp': current_unix_time})

    data_store.set(data)

    return {}

def dm_messages_v1(auth_user_id, given_dm_id, start):
    '''
    Returns last 50 messages from start

    Arguments:
        auth_user_id (integer)  - User Identification Number
        dm_id (integer)         - Dm Identification Number
        start (integer)         - Starting Message
    ...

    Exceptions:
        InputError  - Occurs when
            - dm_id does not refer to a valid DM
            - start is greater than the total number of messages in the channel
        AccessError - Occurs when
            - dm_id is valid and the authorised user is not a member of the DM

    Return Value:
        returns dictionary - {[messages], start, end}
    '''
    data = data_store.get()

    found_dm = [dm for dm in data['dms'] if dm['dm_id'] == given_dm_id]

    # dm_id does not exist
    if len(found_dm) == 0: 
        raise InputError(description="dm_id does not refer to valid dm")

    found_dm = found_dm[0]

    # Check person is member of dm 
    if auth_user_id not in found_dm['users']:
        raise AccessError(description="user not in dm")

    if len(found_dm['messages']) < start:
        raise InputError(description="Start Larger Then Total Messages")

    message_list = []
    for message in found_dm['messages'][start:start+50]:
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

        data_store.set(data)

        return {
            'messages': message_list,
            'start': start,
            'end': start + 50,
        }

    data_store.set(data)

    return {
        'messages': message_list,
        'start': start,
        'end': -1,
    }
    