from src.data import users, channels
from src.error import InputError, AccessError
from src.other import update_data_write, check_session_id


def channels_list_v1(auth_user_id):
    """
    Provides a list of all channels (and their associated details)  
    that the authorised user is part of

    Arguments:
        auth_user_id (int) - ID of the authorised user (who used the feature)

    Exceptions:
        AccessError - Occurs when:
            - auth_user_id is not an integer
            - auth_user_id does not belong to any user

    Returns:
        (dict) containing a list of dictionaries, where each dictionary
        contains the corresponding channel's channel_id and name
    """

    if not type(auth_user_id) == int:
        raise AccessError(description='auth_user_id has to be an integer')

    valid_id = False

    for user in users:
        if user['u_id'] == auth_user_id:
            valid_id = True

    if valid_id == False:
        raise AccessError(description='auth_user_id does not belong to any user')

    list_of_channels = []

    for channel in channels:
        for member in channel['all_members']:
            if member['u_id'] == auth_user_id:
                list_of_channels.append({'channel_id': channel['id'], 'name': channel['name']})

    return {'channels': list_of_channels}


def channels_listall_v1(auth_user_id):
    """
    Provides a list of all channels (and their associated details) 

    Arguments:
        auth_user_id (int) - ID of the authorised user (who used the feature)

    Exceptions:
        AccessError - Occurs when:
            - auth_user_id is not an integer
            - auth_user_id does not belong to any user

    Returns:
        (dict) containing a list of dictionaries, where each dictionary
        contains the corresponding channel's channel_id and name
    """

    if not type(auth_user_id) == int:
        raise AccessError(description='auth_user_id has to be an integer')

    valid_id = False

    for user in users:
        if user['u_id'] == auth_user_id:
            valid_id = True

    if valid_id == False:
        raise AccessError(description='auth_user_id does not belong to any user')

    list_of_channels = []

    for channel in channels:
        list_of_channels.append({'channel_id': channel['id'], 'name': channel['name']})

    return {'channels': list_of_channels}


def channels_create_v1(auth_user_id, name, is_public):
    '''
    Creates a new channel with that name that is either
    a public or private channel 
    
    Arguments:
        auth_user_id (int) - ID of the authorised user (who is creating the channel)  
        name (string) - Name of the channel being created
        is_public (boolean) - If true the channel is public, otherwise the channel is private
    Exceptions:
        InputError occurs when:
            - The given name of the channel exceeds 20 characters
        AccessError occurs when:
            - The authorised user ID is not an integer
            - The authorised user does not exist
    Returns:
        - The channel ID
    '''

    if not type(auth_user_id) == int:
        raise AccessError(description='auth_user_id has to be an integer')

    user_found = False
    for user in users:
        if user['u_id'] == auth_user_id:
            user_found = True

    # Not a valid user
    if user_found is False:
        raise AccessError(description=f"{auth_user_id} is not a valid user ID")

    if len(name) > 20:
        raise InputError(description="The channel name is too long")

    for user in users:
        if user['u_id'] == auth_user_id:
            name_first = user['name_first']
            name_last = user['name_last']
            email = user['email']
            handle = user['handle_str']

    channel_id = len(channels) + 1
    channels.append(
        {
            'id': channel_id, 
            'name': name,
            'is_public': is_public,
            'owner_members': [
                {
                    'u_id': auth_user_id,
                    'email': email,
                    'name_first': name_first,
                    'name_last': name_last,
                    'handle_str': handle,
                },
            ],
            'all_members': [ 
                {
                    'u_id': auth_user_id,
                    'email': email,
                    'name_first': name_first,
                    'name_last': name_last,
                    'handle_str': handle,
                },
            ],
            'messages': [
            ],
            'standup': [
                {
                    'is_active': False,
                    'time_finish': None,
                    'message': ""
                }
            ]
        },
    )

    return {
        'channel_id': channel_id,
    }


def channels_create_v2(token, name, is_public):
    '''
    Creates a new channel with that name that is either
    a public or a private channel 
    
    Arguments:
        token (str) - session token for the logged in user 
        name (string) - Name of the channel being created
        is_public (boolean) - If true the channel is public, otherwise the channel is private
    Exceptions:
        InputError occurs when:
            - The given name of the channel exceeds 20 characters
        AccessError occurs when:
            - The token is invalid
    Returns:
        - The channel ID
    '''

    u_id = check_session_id(token)

    channel_id = channels_create_v1(u_id, name, is_public)

    update_data_write()

    return channel_id


def channels_listall_v2(token):
    """
    Provides a list of all channels (and their associated details) 

    Arguments:
        token (str) - session token for the logged-in user

    Exceptions:
        AccessError - Occurs when:
            - The token is invalid

    Returns:
        (dict) containing a list of dictionaries, where each dictionary
        contains the corresponding channel's channel_id and name
    """

    auth_user_id = check_session_id(token)
    list_of_channels = channels_listall_v1(auth_user_id)

    return list_of_channels


def channels_list_v2(token):
    """
    Provides a list of all channels (and their associated details)
    that the authorised user is part of
    
    
    Arguments:
        token (str) - session token for the logged-in user

    Exceptions:
        AccessError - Occurs when:
            - The token is invalid

    Returns:
        (dict) containing a list of dictionaries, where each dictionary
        contains the corresponding channel's channel_id and name
    """

    auth_user_id = check_session_id(token)
    list_of_channels = channels_list_v1(auth_user_id)

    return list_of_channels
