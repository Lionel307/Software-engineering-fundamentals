from src.data import users, channels
from src.error import InputError, AccessError
from src.other import update_data_write, check_session_id, notifications_added


def channel_invite_v1(auth_user_id, channel_id, u_id):
    '''
    Invites a user (with user id u_id) to join a channel with
    ID channel_id. Once invited the user is added to
    the channel immediately. 

    Arguments:
        u_id (int)- ID of the user who is being invited
        auth_user_id (int) - ID of the authorised user (who invited the user)  
        channel_id (int) - ID of the channel which the invited user is joining

    Exceptions:
        InputError occurs when:
            - The given channel ID does not refer to a valid channel.
            - The user ID does not refer to a valid user
            - The channel ID is not an integer
        AccessError occurs when:
            - the authorised user is not a member of the channel
            - The authorised user ID is not an integer
    Returns:
        - an empty dictionary
    '''

    if not type(auth_user_id) == int:
        raise AccessError(description='auth_user_id has to be an integer')

    if not type(channel_id) == int:
        raise InputError(description='channel_id has to be an integer')

    # Find the details of the user
    user_found = False
    for user in users:
        if user['u_id'] == u_id:
            if not (user['name_first'] == "Removed" and user['name_last'] == "user"):
                user_found = True
                userdata = {
                    'u_id': u_id,
                    'email': user['email'],
                    'name_first': user['name_first'],
                    'name_last': user['name_last'],
                    'handle_str': user['handle_str'],
                }

    # Not a valid user
    if user_found == False:
        raise InputError(description=f"{u_id} is not a valid user ID")

    auth_user_found = False
    invalid_channel = True
    for channel in channels:
        for member in channel['all_members']:
            if member['u_id'] == auth_user_id:
                auth_user_found = True
        if channel['id'] == channel_id:
            invalid_channel = False
    
    # Not a valid channel
    if invalid_channel == True:
        raise InputError(description="Channel id is invalid")

    # Authorised user is not already a member of the channel
    if auth_user_found == False:
        raise AccessError(description=f"{auth_user_id} is not a member of this channel")

    for channel in channels:
        if channel['id'] == channel_id:
            # Function does nothing if the user is already a member of the channel
            for member in channel['all_members']:
                if member['u_id'] == u_id:
                    return {
                    }

            channel['all_members'].append(userdata)

    notifications_added(channel_id, auth_user_id, [u_id], True)
    return {}


def channel_details_v1(auth_user_id, channel_id):
    """
    Given a Channel with ID channel_id that the authorised user, with ID auth_user_id 
    is part of, provide basic details about the channel

    Arguments:
        auth_user_id (int) - ID of the authorised user (who used the feature)  
        channel_id (int) - ID of the channel whose details are to be provided

    Exceptions:
        InputError - Occurs when:
            - channel_id is not an integer
            - channel_id does not refer to any channel
        AccessError - Occurs when:
            - The authorised user is not a member of the channel with channel_id
            - auth_user_id is not an integer
            - auth_user_id does not belong to any user
    
    Returns:
        (dict) containing: 
            - The channel's name
            - A list of dictionaries named owner_members, where each dictionary contains 
            a channel owner's ID u_id, their email, first name, last name and handle
            - A list of dictionaries named all_members, where each dictionary contains 
            a channel member's ID u_id, their email, first name, last name and handle 
    """        

    if not type(auth_user_id) == int:
        raise AccessError(description='auth_user_id has to be an integer')

    valid_user_id = False

    for user in users:
        if user['u_id'] == auth_user_id:
            valid_user_id = True
    
    if valid_user_id == False:
        raise AccessError(description='auth_user_id does not belong to any user')

    if not type(channel_id) == int:
        raise InputError(description='channel_id has to be an integer')
    
    valid_channel_id = False
    channel_name = ''
    list_all_members = []
    list_owner_members = []

    for channel in channels:
        if channel['id'] == channel_id:
            valid_channel_id = True
            channel_name = channel['name']
            list_owner_members = channel['owner_members']
            list_all_members = channel['all_members']
            is_public = channel['is_public']

    if valid_channel_id == False:
        raise InputError(description='channel_id does not refer to any channel')    

    is_member = False
    for member in list_all_members:
        if member['u_id'] == auth_user_id:
            is_member = True

    if is_member == False:
        raise AccessError(description='Authorised user is not a member of channel')

    return {
        'name': channel_name,
        'is_public': is_public,
        'owner_members': list_owner_members,
        'all_members': list_all_members
    }


def channel_messages_v1(auth_user_id, channel_id, start):
    '''
    Given a Channel with ID channel_id that the authorised user is part of, return up to 50 messages 
    between index "start" and "start + 50". Message with index 0 is the most recent message in the channel. 
    This function returns a new index "end" which is the value of "start + 50", or, if this function has 
    returned the least recent messages in the channel, returns -1 in "end" to indicate there are no more 
    messages to load after this return.

    Arguments:
        auth_user_id :: [int] - the user id of user who is calling the function
        channel_id :: [int] - the id of the channel whose messages are to be provided
        start :: [int] - the starting index to return the messages from
    Exceptions:
        InputError - occurs when:
            - Channel ID is not a valid channel
            - Start is greater than the total number of messages in the channel
        AccessError - occurs when:
            - Authorised user is not a member of channel with channel_id
            - auth_user_id is not valid    
    
    Return Value:
        (dict) containing:
            - List of messages
            - Start index
            - Ending index
    '''

    if not type(auth_user_id) == int:
        raise AccessError(description="auth_user_id has to be an integer")

    valid_id = False

    for user in users:
        if user['u_id'] == auth_user_id:
            valid_id = True

    if valid_id == False:
        raise AccessError(description="auth_user_id does not belong to any user")
    
    this_channel = False
    auth_user_in_channel = False
    end = start + 50
    total_messages = 0
    messages = []
    
    for channel in channels:
        if channel['id'] == channel_id:
            this_channel = channel

    if this_channel == False:
        raise InputError(description='channel_id does not refer to any existing channel')


    for auth_user in this_channel['all_members']:
        if auth_user_id == auth_user['u_id']:
            auth_user_in_channel = True
    
    total_messages = len(this_channel['messages'])
    if start > total_messages:
        raise InputError(description="Start is greater than total number of messages")

    r_messages_list = this_channel['messages'].copy()
    r_messages_list.reverse()

    counter = start
    while counter < total_messages and counter < end:
        is_this_user_reacted = False
        if auth_user_id in r_messages_list[counter]["reacts"]:
            is_this_user_reacted = True
        reacts = [
            {
                "react_id": 1,
                "u_ids": r_messages_list[counter]["reacts"],
                "is_this_user_reacted": is_this_user_reacted
            }
        ]

        append_this = {
            "message_id": r_messages_list[counter]["message_id"],
            "u_id": r_messages_list[counter]["u_id"],
            "message": r_messages_list[counter]["message"],
            "time_created": r_messages_list[counter]["time_created"],
            "reacts": reacts,
            "is_pinned": r_messages_list[counter]["is_pinned"]
        }

        messages.append(append_this)
        counter = counter + 1


    if end >= total_messages:
        end = -1
    

    if auth_user_in_channel == False:
        raise AccessError(description='Authorised user is not a member of this channel')
    

    return {
        'messages': messages,
        'start': start,
        'end': end,
    }


def channel_leave_v1(token, channel_id):
    """
    Given a channel ID, the user removed as a member of this channel. 
    Their messages still remain in the channel

    Arguments:
        token (str) - session token for the logged in user calling the function
        channel_id (int) - ID of the channel whose owner will be removed

    Exceptions:
        InputError - Occurs when:
            - channel_id is not a valid channel
        AccessError - Occurs when:
            - The token is not a valid id
            - The authorised user is not a member of the channel with channel_id

    Return Value:
        {}
    """

    try:
        auth_user_id = check_session_id(token)
    except Exception:
        raise AccessError(description="Invalid token") from Exception

    valid_channel = False
    for channel in channels:
        if channel['id'] == channel_id:
            valid_channel = True
            list_owners = channel['owner_members']
            list_members = channel['all_members']

    if valid_channel == False:
        raise InputError(description=f"{channel_id} is not a valid channel")

    valid_member = False
    for idx, member in enumerate(list_members):
        if member['u_id'] == auth_user_id:
            valid_member = True
            member_at_index = idx

    if valid_member == False:
        raise AccessError(description="The authorised user is not a member of the channel")

    # remove the member from the list of all members
    del list_members[member_at_index]

    # remove the member from the list of owners, if they are an owner of the channel
    for idx, owner in enumerate(list_owners):
        if owner['u_id'] == auth_user_id:
            del list_owners[idx]

    update_data_write()
    
    return {}


def channel_join_v1(auth_user_id, channel_id):
    '''
    Given a channel_id of a channel that the authorised user can join, adds them to that channel

    Arguments:
        auth_user_id :: [int] - the user id of user who is calling the function
        channel_id :: [int] - the id of the channel to join
    Exceptions:
        InputError - occurs when:
            - Channel ID is not a valid channel
        AccessError - occurs when:
            - channel_id refers to a channel that is private (when the authorised user is not a global owner)
            - auth_user_id is not valid
    Return Value:
        {}
    '''

    if not type(auth_user_id) == int:
        raise AccessError(description='auth_user_id has to be an integer')

    valid_id = False

    for user in users:
        if user['u_id'] == auth_user_id:
            valid_id = True
    
    if valid_id == False:
        raise AccessError(description='auth_user_id does not belong to any user')

    for user in users:
        if user['u_id'] == auth_user_id:
            userdata = user

    new_user = {
        'u_id': userdata['u_id'],
        'email': userdata['email'],
        'name_first': userdata['name_first'],
        'name_last': userdata['name_last'],
        'handle_str': userdata['handle_str'],
    }

    flag = False
    for channel in channels:
        if channel['id'] == channel_id:
            # Function does nothing if the user is already a member of the channel
            for member in channel['all_members']:
                if member['u_id'] == new_user['u_id']:
                    return {
                    }

            if channel['is_public'] == False and userdata['permission_id'] != 1:
                raise AccessError(description="Channel is private")

            # Adds the new member to the channel 
            channel['all_members'].append(new_user)
            flag = True
            break

    if flag == False:
        raise InputError(description="Channel ID is not a valid channel")

    return {
    }


def channel_join_v2(token, channel_id):
    '''
    Given a channel_id of a channel that the authorised user can join, adds them to that channel

    Arguments:
        token :: [str] - session token for the logged in user 
        channel_id :: [int] - the id of the channel to join
    Exceptions:
        InputError - occurs when:
            - Channel ID is not a valid channel
        AccessError - occurs when:
            - channel_id refers to a channel that is private (when the authorised user is not a global owner)
            - token is not valid
    Return Value:
        {}
    '''

    u_id = check_session_id(token)

    channel_join_v1(u_id, channel_id)

    update_data_write()

    return {}


def channel_details_v2(token, channel_id):
    """
    Given a Channel with ID channel_id that the authorised user is part of, 
    provide basic details about the channel

    Arguments:
        token :: [str] - session token for the logged in user 
        channel_id :: [int] - ID of the channel whose details are to be provided

    Exceptions:
        InputError - Occurs when:
            - channel_id is not an integer
            - channel_id does not refer to any channel
        AccessError - Occurs when:
            - The authorised user is not a member of the channel with channel_id
            - token is invalid
    
    Returns:
        (dict) containing: 
            - The channel's name
            - A list of dictionaries named owner_members, where each dictionary contains 
            a channel owner's ID u_id, their email, first name, last name and handle
            - A list of dictionaries named all_members, where each dictionary contains 
            a channel member's ID u_id, their email, first name, last name and handle 
    """       
    

    u_id = check_session_id(token)

    details = channel_details_v1(u_id, channel_id)

    return details


def channel_messages_v2(token, channel_id, start):
    '''
    Given a Channel with ID channel_id that the authorised user is part of, return up to 50 messages 
    between index "start" and "start + 50". Message with index 0 is the most recent message in the channel. 
    This function returns a new index "end" which is the value of "start + 50", or, if this function has 
    returned the least recent messages in the channel, returns -1 in "end" to indicate there are no more 
    messages to load after this return.

    Arguments:
        token :: [str] - session token for the logged in user calling the function
        channel_id :: [int] - the id of the channel whose messages are to be provided
        start :: [int] - the starting index to return the messages from
    Exceptions:
        InputError - occurs when:
            - Channel ID is not a valid channel
            - Start is greater than the total number of messages in the channel
        AccessError - occurs when:
            - Authorised user is not a member of channel with channel_id
            - Token is not valid    
    
    Return Value:
        (dict) containing:
            - List of messages
            - Start index
            - Ending index
    '''

    u_id = check_session_id(token)

    return_value = channel_messages_v1(u_id, channel_id, start)

    return return_value


def channel_addowner_v1(token, channel_id, u_id):
    """
    Make user with user id u_id an owner of the channel channel_id

    Arguments:
        token (str) - session token for the logged in user calling the function
        channel_id (int) - ID of the channel where the user will become an owner
        u_id (int) - ID of the user who is to become an owner of the channel

    Exceptions:
        InputError - Occurs when:
            - channel_id is not a valid channel
            - The user with user id u_id is already an owner of the channel
            - The user with user id u_id is not a member of the channel
        AccessError - Occurs when:
            - The token is not a valid id
            - The authorised user is not an owner of Dreams or an owner of the channel
    
    Return Value:
        {}
    """

    try:
        auth_user_id = check_session_id(token)
    except Exception:
        raise AccessError(description = "Invalid token") from Exception

    valid_channel_id = False
    for channel in channels:
        if channel['id'] == channel_id:
            valid_channel_id = True
            list_owners = channel['owner_members']
            list_members = channel['all_members']

    if valid_channel_id == False:
        raise InputError(description = "The channel_id is not valid")

    auth_is_owner = False
    # Checks if the authorised user is a Dreams owner
    for user in users:
        if user['u_id'] == auth_user_id:
            if user['permission_id'] == 1:
                auth_is_owner = True

    for owner in list_owners:
        if owner['u_id'] == u_id:
            raise InputError(description = "The user with user id u_id is "
                                           "already an owner of this channel")

        if owner['u_id'] == auth_user_id:
            auth_is_owner = True

    if auth_is_owner == False:
        raise AccessError(description = "The authorised user is not an owner" 
                                        " of Dreams or of this channel")

    user_is_member = False
    for member in list_members:
        if member['u_id'] == u_id:
            user_is_member = True
            user_details = member

    if user_is_member == False:
        raise InputError(description = "The user with user id u_id is"
                                       " not a member of this channel")

    list_owners.append(user_details)

    update_data_write()

    return {}


def channel_removeowner_v1(token, channel_id, u_id):
    """
    Remove user with user id u_id an owner of the channel channel_id

    Arguments:
        token (str) - session token for the logged in user calling the function
        channel_id (int) - ID of the channel whose owner will be removed
        u_id (int) - ID of the user who is to be removed as an owner of the channel

    Exceptions:
        InputError - Occurs when:
            - channel_id is not a valid channel
            - The user with user id u_id is not an owner of the channel
            - The user is currently the only owner
        AccessError - Occurs when:
            - The token is not a valid id
            - The authorised user is not an owner of Dreams or an owner of the channel

    Return Value:
        {}
    """

    try:
        auth_user_id = check_session_id(token)
    except Exception:
        raise AccessError(description = "Invalid token") from Exception

    valid_channel_id = False
    for channel in channels:
        if channel['id'] == channel_id:
            valid_channel_id = True
            list_owners = channel['owner_members']

    if valid_channel_id == False:
        raise InputError(description = "The channel_id is not valid")

    auth_is_owner = False
    # Checks if the authorised user is a Dreams owner
    for user in users:
        if user['u_id'] == auth_user_id:
            if user['permission_id'] == 1:
                auth_is_owner = True

    is_channel_owner = False
    for idx, owner in enumerate(list_owners):
        if owner['u_id'] == u_id:
            is_channel_owner = True
            matching_index = idx

        if owner['u_id'] == auth_user_id:
            auth_is_owner = True

    if auth_is_owner == False:
        raise AccessError(description = "The authorised user is not an owner"
                                        " of Dreams or of this channel")

    if is_channel_owner == False:
        raise InputError(description = "The user with user id u_id is not an"
                                       " owner of the channel")
    
    if len(list_owners) == 1:
        raise InputError(description = "The user is currently the only owner")

    list_owners.pop(matching_index)

    update_data_write()

    return {}


def channel_invite_v2(token, channel_id, u_id):
    '''
    Invites a user (with user id u_id) to join a channel with
    ID channel_id. Once invited the user is added to
    the channel immediately. 

    Arguments:
        token (str) - session token for the logged in user calling the function  
        channel_id (int) - ID of the channel which the invited user is joining
        u_id (int) - ID of the user who is being invited

    Exceptions:
        InputError occurs when:
            - The given channel ID does not refer to a valid channel.
            - The user ID does not refer to a valid user
        AccessError occurs when:
            - The token is not a valid id
            - the authorised user is not a member of the channel
            
    Return Value:
        {}
    '''
    
    auth_user_id = check_session_id(token)

    channel_invite_v1(auth_user_id, channel_id, u_id)

    update_data_write()

    return {}
