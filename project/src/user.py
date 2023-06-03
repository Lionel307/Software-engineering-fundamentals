import re

from src.data import users, channels, dms, sessions
import src.other
from src.error import InputError, AccessError


def user_profile_setname_v2(token, name_first, name_last):
    '''
    Update the authorised user's first and last name

    Arguments:
        token :: [str] - Session token of logged in user calling the function
        name_first :: [str] - The user's first name
        name_last :: [str] - The user's last name

    Exceptions:
        InputError - Occurs when:
            - name_first is not between 1 and 50 characters inclusively in length
            - name_last is not between 1 and 50 characters inclusively in length
        AccessError - Occurs when:
            - token in invalid

    Return Value:
        {} - Empty dictionary
    '''

    if(len(name_first) < 1 or len(name_first) > 50 or len(name_last) < 1 or len(name_last) > 50):
        raise InputError(description="First last names must each be >0 and <51 characters long")

    u_id = src.other.check_session_id(token)

    for profile in users:
        if profile["u_id"] == u_id:
            profile["name_first"] = name_first
            profile["name_last"] = name_last

    for channel in channels:
        for user in channel["owner_members"]:
            if user["u_id"] == u_id:
                user["name_first"] = name_first
                user["name_last"] = name_last
        for user in channel["all_members"]:
            if user["u_id"] == u_id:
                user["name_first"] = name_first
                user["name_last"] = name_last

    for dm in dms:
        for user in dm["owner_members"]:
            if user["u_id"] == u_id:
                user["name_first"] = name_first
                user["name_last"] = name_last
        for user in dm["all_members"]:
            if user["u_id"] == u_id:
                user["name_first"] = name_first
                user["name_last"] = name_last

    src.other.update_data_write()
    return {
    }


def user_profile_setemail_v2(token, email):
    '''
    Update the authorised user's email address

    Arguments:
        token :: [str] - Session token of logged in user calling the function
        email :: [str] - The user's new email address

    Exceptions:
        InputError - Occurs when:
            - Email entered is not a valid email
            - Email address is already being used by another user
        AccessError - Occurs when:
            - token in invalid

    Return Value:
        {} - Empty dictionary
    '''

    u_id = src.other.check_session_id(token)

    regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'
    if not re.search(regex, email):
        raise InputError(description="Invalid Email")

    for profile in users:
        if profile["email"].lower() == email.lower() and \
        not (profile["name_first"] == "Removed" and profile["name_last"] == "user"):
            raise InputError(description="Email address is already in use")

    for profile in users:
        if profile["u_id"] == u_id:
            profile["email"] = email

    for channel in channels:
        for user in channel["owner_members"]:
            if user["u_id"] == u_id:
                user["email"] = email
        for user in channel["all_members"]:
            if user["u_id"] == u_id:
                user["email"] = email

    for dm in dms:
        for user in dm["owner_members"]:
            if user["u_id"] == u_id:
                user["email"] = email
        for user in dm["all_members"]:
            if user["u_id"] == u_id:
                user["email"] = email

    src.other.update_data_write()

    return {
    }


def user_profile_sethandle_v1(token, handle_str):
    '''
    Update the authorised user's handle (i.e. display name)

    Arguments:
        token :: [str] - Session token of logged in user calling the function
        handle_str :: [str] - The user's new handle

    Exceptions:
        InputError - Occurs when:
            - handle_str is not between 3 and 20 characters inclusive in length
            - handle is already used by another user
        AccessError - Occurs when:
            - token in invalid

    Return Value:
        {} - Empty dictionary
    '''

    u_id = src.other.check_session_id(token)

    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(description="Handle must be between 3 and 20 characters inclusive in length")

    for profile in users:
        if profile["handle_str"] == handle_str:
            raise InputError(description="Handle is already in use")

    for profile in users:
        if profile["u_id"] == u_id:
            profile["handle_str"] = handle_str

    for channel in channels:
        for user in channel["owner_members"]:
            if user["u_id"] == u_id:
                user["handle_str"] = handle_str
        for user in channel["all_members"]:
            if user["u_id"] == u_id:
                user["handle_str"] = handle_str

    for dm in dms:
        for user in dm["owner_members"]:
            if user["u_id"] == u_id:
                user["handle_str"] = handle_str
        for user in dm["all_members"]:
            if user["u_id"] == u_id:
                user["handle_str"] = handle_str

    src.other.update_data_write()

    return {
    }


def user_profile_v2(token, u_id):
    """
    For a valid user, returns information about their user_id, email, first name, last name, and handle

    Arguments:
        token :: [str] - session token for user calling the function
        u_id :: [int] - user id of the specified user
    
    Exceptions:
        InputError - Occurs when:
            - User with u_id is not a valid user
        AccessError - Occurs when:
            - token in invalid

    Return Value:
        {user} - where user is a dictionary containing u_id, email, name_first, name_last, handle_str
    """

    src.other.check_session_id(token)

    user_profile = False
    for profile in users:
        if profile["u_id"] == u_id:
            user_profile = profile
    
    if user_profile == False:
        raise InputError(description="User with u_id is not a valid user")

    user = {
        "u_id": user_profile["u_id"],
        "email": user_profile["email"],
        "name_first": user_profile["name_first"],
        "name_last": user_profile["name_last"],
        "handle_str": user_profile["handle_str"],
    }

    return {
        "user": user
    }


def admin_userpermission_change_v1(token, u_id, permission_id):
    """
    Given a User by their user ID, set their permissions to new permissions described by permission_id

    Arguments:
        token :: [str] - session token for user calling the function
        u_id :: [int] - user id of the specified user
        permission_id :: [int] - the new permission_id of the specified user
    
    Exceptions:
        InputError - Occurs when:
            - User with u_id is not a valid user
            - permission_id does not refer to a valid permission
        AccessError - Occurs when:
            - token in invalid
            - The authorised user is not an owner

    Return Value:
        {}
    """

    auth_user_id = src.other.check_session_id(token)


    if permission_id != 1  and permission_id != 2:
        raise InputError(description="permission_id does not refer to a valid permission")

    is_owner = False
    valid_user = False
    for user in users:
        if user["u_id"] == auth_user_id:
            if user["permission_id"] == 1:
                is_owner = True
        if user["u_id"] == u_id: 
            if not (user['name_first'] == "Removed" and user['name_last'] == "user"):
                valid_user = True

    if is_owner == False:
        raise AccessError(description="The authorised user is not an owner")
    
    if valid_user == False:
        raise InputError(description="User with u_id is not a valid user")

    for user in users:
        if user["u_id"] == u_id:
            user["permission_id"] = permission_id


    src.other.update_data_write()
    return {

    }


def users_all_v1(token):
    """
    Returns a list of all users and their associated details

    Arguments:
        token (str) - session token for the logged in user calling the function

    Exceptions:
        AccessError - Occurs when:
            - The token is not a valid id

    Returns:
        users (dict) containing a list of dictionaries where each dictionary
        contains the corresponding user's:
            - u_id
            - email
            - name_first
            - name_last
            - handle_str
    """

    src.other.check_session_id(token)

    list_users = []

    for user in users:
        if not (user["name_first"] == "Removed" and user["name_last"] == "user"):
            list_users.append(
                {
                    'u_id': user['u_id'],
                    'email': user['email'],
                    'name_first': user['name_first'],
                    'name_last': user['name_last'],
                    'handle_str': user['handle_str']
                }
            )

    return {
        'users': list_users
    }


def admin_user_remove_v1(token, u_id):
    """
    Removes the user with the user id u_id from Dreams

    Arguments:
        token (str) - session token for the logged in user calling the function
        u_id (int) - ID of the user who is to be removed

    Exceptions:
        InputError - Occurs when:
            - The user with u_id is not a valid user
            - The user is currently the only owner of Dreams
        AccessError - Occurs when:
            - The token is not a valid id
            - The authorised user is not an owner of Dreams

    Return Value:
        {}
    """

    auth_user_id = src.other.check_session_id(token)

    is_owner = False
    valid_user = False
    num_owners = 0

    for idx, user in enumerate(users):
        if user["u_id"] == auth_user_id:
            if user["permission_id"] == 1:
                is_owner = True
        
        if user["u_id"] == u_id and not (user["name_first"] == "Removed" and \
        user["name_last"] == "user"):
            valid_user = True
            remove_idx = idx

        if user["permission_id"] == 1 and not (user["name_first"] == "Removed" and \
        user["name_last"] == "user"):
            num_owners += 1

    if is_owner == False:
        raise AccessError(description="The authorised user is not an owner")
    
    if valid_user == False:
        raise InputError(description="User with u_id is not a valid user")    

    if num_owners == 1 and auth_user_id == u_id:
        raise InputError(description="The user is currently the only owner")

    users[remove_idx]['name_first'] = "Removed"
    users[remove_idx]['name_last'] = "user"

    new_sessions_list = []
    for user in sessions:
        if not user["u_id"] == u_id:
            new_sessions_list.append(user)

    # rebuild the list of sessions which does not contain the removed user's sessions  
    sessions.clear()
    sessions.extend(new_sessions_list)

    for channel in channels:
        new_channel_members = []
        new_channel_owners = []

        for message in channel['messages']:
            if message['u_id'] == u_id:
                message['message'] = 'Removed user'

        for member in channel['all_members']:
            if not member['u_id'] == u_id:
                new_channel_members.append(member)

        # rebuild the list of channel members which does not contain the removed user
        channel['all_members'].clear()
        channel['all_members'].extend(new_channel_members)

        for owner in channel['owner_members']:
            if not owner['u_id'] == u_id:
                new_channel_owners.append(owner)

        # rebuild the list of channel owners which does not contain the removed user
        channel['owner_members'].clear()
        channel['owner_members'].extend(new_channel_owners)

    for dm in dms:
        new_dm_members = []
        new_dm_owners = []

        for message in dm['messages']:
            if message['u_id'] == u_id:
                message['message'] = 'Removed user'

        for member in dm['all_members']:
            if not member['u_id'] == u_id:
                new_dm_members.append(member)

        # rebuild the list of dm members which does not contain the removed user
        dm['all_members'].clear()
        dm['all_members'].extend(new_dm_members)

        for owner in dm['owner_members']:
            if not owner['u_id'] == u_id:
                new_dm_owners.append(owner)

        # rebuild the list of dm owners which does not contain the removed user
        dm['owner_members'].clear()
        dm['owner_members'].extend(new_dm_owners)

    src.other.update_data_write()

    return {}
