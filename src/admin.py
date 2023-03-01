from src.channel import channel_leave_v1

from src.dm import dm_leave_v1
from src.helpers import get_full_user_object
from src.data_store import data_store
from src.error import AccessError, InputError


def admin_user_remove_v1(auth_user_id, u_id):
    '''
    This function removes the user from Seams.

    Arguments:
        auth_user_id    (integer)    - User ID with global owner permissions
        u_id            (integer)    - User ID to remove

    Exceptions:
        InputError
            - Occurs when any of:
                - u_id does not refer to a valid user
                - u_id refers to a user who is the only global owner
        AccessError
            - Occurs when any of:
                - the authorised user is not a global owner

    Return Value:
        Returns {} (dictionary) on successful user removal
    '''
    store = data_store.get()

    
    # for user in store['users']:
    #     if user['user_id'] == auth_user_id:
    #         if user['global_perm'] == 2:
    #             raise AccessError(description='You are not a global owner.')
    #         break

    # Check if authorised user is a global owner
    user = get_full_user_object(auth_user_id)
    if user['global_perm'] == 2:
        raise AccessError(description='You are not a global owner.')
    
    # Check if u_id is a valid user id
    for user in store['users']:
        if user['user_id'] == u_id:

            # Check if u_id is not the only global owner
            for u in store['users']:
                if u['user_id'] != u_id and u['global_perm'] == 1:

                    # Rename user to 'Removed user'
                    user['name_first'] = 'Removed'
                    user['name_last'] = 'user'

                    # Remove all sessions
                    user['sessions'] = []

                    # Declare user as removed
                    user['removed'] = True

                    for channel in store['channels']:
                        for message in channel['messages']:
                                if u_id == message['u_id']:
                                    message['message'] = 'Removed user'

                    for dm in store['dms']:
                        for message in dm['messages']:
                                if u_id == message['u_id']:
                                    message['message'] = 'Removed user'

                    data_store.set(store)
                    
                    # Leave all channels
                    for channel in store['channels']:
                        if u_id in channel['all_members_id']:
                            channel_leave_v1(u_id, channel['channel_id'])

                            # # Replace user messages in channel with 'Removed user'
                            # for message in channel['messages']:
                            #     if u_id == message['u_id']:
                            #         message['message'] = 'Removed user'

                    for dm in store['dms']:
                        if u_id in dm['users']:
                            dm_leave_v1(u_id, dm['dm_id'])

                    # data_store.set()
                    return {}
                        
            raise InputError(description='The provided u_id is the only global owner.')
    
    raise InputError(description='The provided u_id is not a valid user id.')


def admin_userpermission_change_v1(auth_user_id, u_id, permission_id):
    '''
    This function changes the user's permission id.

    Arguments:
        auth_user_id    (integer)    - User ID with global permisions
        u_id            (integer)    - User ID to change permission_id
        permission_id   (integer)    - Permission ID

    Exceptions:
        InputError
            - Occurs when any of:
                - u_id does not refer to a valid user
                - u_id refers to a user who is the only global owner and they are being demoted to a user
                - permission_id is invalid
                - the user already has the permissions level of permission_id
        AccessError
            - Occurs when any of:
                - the authorised user is not a global owner

    Return Value:
        Returns {} (dictionary) on successful user permission change
    '''
    store = data_store.get()

    # Check if authorised user is a global owner
    user = get_full_user_object(auth_user_id)
    if user['global_perm'] == 2:
        raise AccessError(description='You are not a global owner.')

    # Check if permission id is valid
    if permission_id not in {1, 2}:
        raise InputError(description='The provided permission_id is invalid.')
    
    # Check if u_id is a valid user id
    for user in store['users']:
        if user['user_id'] == u_id:
            
            # Check if u_id is not the only global owner
            for u in store['users']:
                if u['user_id'] != u_id and u['global_perm'] == 1:
                    
                    # Check if the provided permission id is the same as existing.
                    if user['global_perm'] != permission_id:
                        user['global_perm'] = permission_id
                        data_store.set(store)
                        return {}
                
                    raise InputError(description='The provided u_id already has the permission of permission_id.')

            raise InputError(description='The provided u_id is the only global owner.')
    
    raise InputError(description='The provided u_id is not a valid user id.')

