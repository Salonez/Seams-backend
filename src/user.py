import re
import urllib.request
from urllib.parse import urlparse
from os.path import splitext
from PIL import Image

from src.data_store import data_store
from src.error import InputError
from src.config import url
from src.helpers import get_user_output


def users_all_v1():
    '''
    This function returns a list of all users and their associated details.

    Arguments:
        None

    Exceptions:
        None

    Return Value:
        - List of Users (List)
    '''
    store = data_store.get()

    user_details_list = []

    for user in store['users']:
        if user['removed'] is True:
            continue

        user_details_list.append(get_user_output(user['user_id']))
    
    return {
        'users': user_details_list
    }


def user_profile_v1(u_id):
    '''
    This function returns information about a user.

    Arguments:
        u_id            (integer)    - User ID

    Exceptions:
        InputError
            - Occurs when any of:
                - u_id does not refer to a valid user

    Return Value:
        - User (dictionary)
    '''
    # store = data_store.get()
    # for user in store['users']:
    #     if u_id == user['user_id']:
    #         return {
    #             'user': get_user_output(user['user_id'])
    #         }

    user_output = get_user_output(u_id)

    if not user_output:
        raise InputError(description='The provided user id does not refer to a valid user.')
    
    return {'user': user_output}


def user_profile_setname_v1(auth_user_id, name_first, name_last):
    '''
    This function sets the authenticated user's first name and last name.

    Arguments:
        auth_user_id            (integer)    - Authenticated User ID
        name_first              (string)     - First Name
        name_last               (string)     - Last Name

    Exceptions:
        InputError
            - Occurs when any of:
                - length of name_first is not between 1 and 50 characters inclusive
                - length of name_last is not between 1 and 50 characters inclusive

    Return Value:
        Returns {} (dictionary) on successful name change
    '''
    store = data_store.get()

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

    for user in store['users']:
        if auth_user_id == user['user_id']:
            user['name_first'] = name_first
            user['name_last'] = name_last
            data_store.set(store)
    
    return {}


def user_profile_setemail_v1(auth_user_id, email):
    '''
    This function sets the authenticated user's email.

    Arguments:
        auth_user_id            (integer)    - Authenticated User ID
        email                   (string)     - Email Address

    Exceptions:
        InputError
            - Occurs when any of:
                - email entered is not a valid email
                - email address is already being used by another user

    Return Value:
        Returns {} (dictionary) on successful email change
    '''
    store = data_store.get()

    # Check if the provided email is a valid email address
    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.fullmatch(email_regex, email):
        raise InputError(description='The provided email is not a valid email address.')

    # Check if the provided email is already in use
    for user in store['users']:
        if user['user_id'] != auth_user_id and user['email'] == email and user['removed'] is False:
            raise InputError(description='The provided email is already in use.')

    for user in store['users']:
        if auth_user_id == user['user_id']:
            user['email'] = email
            data_store.set(store)

    return {}


def user_profile_sethandle_v1(auth_user_id, handle_str):
    '''
    This function sets the authenticated user's email.

    Arguments:
        auth_user_id            (integer)    - Authenticated User ID
        handle_str              (string)     - Handle

    Exceptions:
        InputError
            - Occurs when any of:
                - length of handle_str is not between 3 and 20 characters inclusive
                - handle_str contains characters that are not alphanumeric
                - the handle is already used by another user

    Return Value:
        Returns {} (dictionary) on successful handle change
    '''
    # Check if handle is within range
    if len(handle_str) < 3:
        raise InputError(description='Your handle needs to be at least 2 characters.')
    if len(handle_str) > 20:
        raise InputError(description='Your handle must be within 20 characters.')
    
    # Check if handle contains non alphanumeric characters
    if handle_str.isalnum() is False:
        raise InputError(description='Your handle must not contain any alphanumeric characters.')

    store = data_store.get()
    
    # Check if handle is used by another user
    for user in store['users']:
        if user['user_id'] != auth_user_id and user['handle_str'] == handle_str and user['removed'] is False:
            raise InputError(description='The provided handle is already in use.')
    
    for user in store['users']:
        if auth_user_id == user['user_id']:
            user['handle_str'] = handle_str
            data_store.set(store)

    return {}

def user_stats_v1(auth_user_id):
    '''
    Fetches the required statistics about this user's use of UNSW Seams.

    Arguments:
        auth_user_id            (integer)    - Authenticated User ID

    Exceptions:
        None

    Return Value:
        Returns {'user_stats'}
    '''
    store = data_store.get()
    user_stats = store['user_stats'][auth_user_id]

    user_channels = user_stats['channels_joined'][-1]['num_channels_joined']
    user_dms = user_stats['dms_joined'][-1]['num_dms_joined']
    user_messages = user_stats['messages_sent'][-1]['num_messages_sent']

    # Calculating involvement
    if store['channels'] != [] or store['dms'] != []:
        total_channels = len(store['channels'])
        total_channel_msg = 0
        for channel in store['channels']:
            total_channel_msg += len(channel['messages'])
        total_dms = len(store['dms'])
        total_dm_msg = 0
        for dm in store['dms']:
            total_dm_msg += len(dm['messages'])
        top = user_channels + user_dms + user_messages
        bot = total_channels + total_dms + total_channel_msg + total_dm_msg
        involve = top / bot
        if involve > 1:
            involve = 1
        user_stats['involvement_rate'] = involve

    print({'user_stats': user_stats})
    return {'user_stats': user_stats}

def users_stats_v1(auth_user_id):
    '''
    Fetches the required statistics about the use of UNSW Seams.

    Arguments:
        auth_user_id            (integer)    - Authenticated User ID

    Exceptions:
        None

    Return Value:
        Returns {'workspace_stats'}
    '''
    store = data_store.get()
    
    # Caclulating utilization
    user_count = 0
    num_user_in_channel_or_dm = 0
    for user in store['users']:
        user_count += 1
        found_channel = False
        for channel in store['channels']:
            if user['user_id'] in channel['all_members_id']:
                num_user_in_channel_or_dm += 1
                found_channel = True
                break
        if found_channel == False:
            for dm in store['dms']:
                if user['user_id'] in dm['users'] or user == dm['owner']:
                    num_user_in_channel_or_dm += 1
                    break
    workspace_stats = store['workspace_stats']
    workspace_stats['utilization_rate'] = num_user_in_channel_or_dm / user_count

    return {'workspace_stats': workspace_stats}


def user_profile_uploadphoto_v1(auth_user_id, img_url, x_start, y_start, x_end, y_end):
    '''
    This function updates the user profile photo.

    Arguments:
        auth_user_id        (string)    - Authenticated User ID
        img_url             (string)    - Image URL
        x_start             (integer)   - Start Bound on x-axis
        y_start             (integer)   - Start Bound on y-axis
        x_end               (integer)   - End Bound on x-axis
        y_end               (integer)   - End Bound on y-axis

    Exceptions:
        InputError
            - Occurs when any of:
                - img_url returns an HTTP status other than 200, or any other errors occur when attempting to retrieve the image
                - any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
                - x_end is less than or equal to x_start or y_end is less than or equal to y_start
                - image uploaded is not a JPG
    Return Value:
        Returns {} (dictionary) on successful user profile photo upload
    '''
    
    parsed = urlparse(img_url)
    _, ext = splitext(parsed.path)
    if ext not in ['.jpg', '.jpeg']:
        raise InputError(description='img_url is not a jpg file.')

    if x_start < 0 or y_start < 0 or x_end < 0 or y_end < 0:
        raise InputError(description="bounds can't be negative values")

    if x_start >= x_end or y_start >= y_end:
        raise InputError(description="start bounds can't be larger than end")

    image_directory = f'user_profile_images/{auth_user_id}.jpg'

    try:
        urllib.request.urlretrieve(img_url, image_directory)
    except Exception as error:
        raise InputError(description='img_url is invalid') from error

    image_object = Image.open(image_directory)

    image_width, image_height = image_object.size
    if image_width < x_end or image_height < y_end:
        raise InputError(description="bounds can't be larger than image")

    cropped_image = image_object.crop((x_start, y_start, x_end, y_end))
    cropped_image.save(image_directory)
    
    store = data_store.get()

    for user in store['users']:
        if user['user_id'] == auth_user_id:
            user['profile_img_url'] = f'{url}user/profile/image/{auth_user_id}.jpg'
    
    data_store.set(store)
    
    return {}
