from src.data_store import data_store
from src.error import InputError
from src.helpers import is_reacted


def search_v1(auth_user_id, query_str):
    '''
    This function returns a collection of messages in all of the channels/DMs that the user has joined that contain the query.

    Arguments:
        auth_user_id    (integer)    - Authenticated User ID
        query_str       (string)     - Query String

    Exceptions:
        InputError
            - Occurs when any of:
                - length of query_str is less than 1 or over 1000 characters

    Return Value:
        dictionary of { messages }
    '''

    if len(query_str) < 1 or len(query_str) > 1000:
        raise InputError(description='query string not within limits')
        
    store = data_store.get()

    search_results = []

    for channel in store['channels']:

        # If user is not part of channel, skip
        if auth_user_id not in channel['all_members_id']:
            continue
        
        for message in channel['messages']:

            # If message contains query string
            if message['message'].lower().find(query_str.lower()) != -1:
                search_results.append({
                    'message_id': message['message_id'],
                    'u_id': message['u_id'],
                    'message': message['message'],
                    'time_sent': message['time_sent'],
                })
            
    for dm in store['dms']:

        # If user is not part of dm, skip
        if auth_user_id not in dm['users']:
            continue

        for message in dm['messages']:

            # If message contains query string
            if message['message'].lower().find(query_str.lower()) != -1:
                search_results.append({
                    'message_id': message['message_id'],
                    'u_id': message['u_id'],
                    'message': message['message'],
                    'time_sent': message['time_sent'],
                    'reacts' : [{
                        'react_id' : 1,
                        'u_ids' : [ item['u_id'] for item in message['reacts'] ],
                        'is_this_user_reacted' : is_reacted(auth_user_id, message, 1)
                    }],
                    'is_pinned': message['is_pinned']
                })

    return {
        'messages': search_results
    }
