from src.error import AccessError, InputError
from src.data_store import data_store

def get_notifications_v1(auth_user_id):
    '''
    Return the user's most recent 20 notifications, ordered from most recent to least recent.

    Arguments:
        auth_user_id            (integer)    - Authenticated User ID

    Exceptions:
        None

    Return Value:
        Returns {'notifications'}
    '''
    notifications = []
    store = data_store.get()
    num_notif = len(store['notifications'][auth_user_id])
    if num_notif > 0:
        i = -1
        while i > -21:
            notifications.append(store['notifications'][auth_user_id][i])
            i = i - 1
            if num_notif + i < 0:
                break
    
    return {
        'notifications': notifications
    }
