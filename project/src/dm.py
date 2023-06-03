import uuid

from src.data import users, dms
from src.error import InputError, AccessError
from src.other import update_data_write, check_session_id, notifications_added


def dm_create_v1(token, u_ids):
    '''
    Creates a new DM with name that generated based on the user(s) in the DM
    Arguments:
        token (str) - session token for the logged in user 
        u_ids (list) - list of user ids
    Exceptions:
        InputError when:
            - u_id does not refer to a valid user
        AccessError occurs when:
            - The token is not valid

    Returns:
        - the ID of the new DM and name of it
    '''

    auth_user_id = check_session_id(token)

    for user in users:
        if user['u_id'] == auth_user_id:
            dm_creator_data = {
                'u_id': auth_user_id,
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle_str'],
            }

    dm_name = []
    dm_name.append(dm_creator_data['handle_str'])

    list_members = [dm_creator_data]

    u_id_found = False
    for u_id in u_ids:
        for user in users:
            # the user is counted as invalid if they have been removed from Dreams
            if user['u_id'] == u_id and not (user["name_first"] == "Removed" and
                                             user["name_last"] == "user"):
                u_id_found = True

                dm_name.append(user['handle_str'])
                list_members.append(
                    {
                        'u_id': u_id,
                        'email': user['email'],
                        'name_first': user['name_first'],
                        'name_last': user['name_last'],
                        'handle_str': user['handle_str'],
                    }
                )

        if u_id_found is False:
            raise InputError(description="u_id does not refer to a valid user")

    last_dm_id = 0

    # if the list of dms is not empty
    if dms:
        last_dm = dms[-1]
        last_dm_id = last_dm["id"]

    dm_id = last_dm_id + 1
    dm_name = sorted(dm_name)
    name = ", ".join(dm_name)

    dms.append(
        {
        'id': dm_id,
        'name': name,
        'owner_members': [dm_creator_data],
        'all_members': list_members,
        'messages': [],
        },
    )
    notifications_added(dm_id, auth_user_id, u_ids, False)

    update_data_write()

    return {
        'dm_id': dm_id,
        'dm_name': name
    }


def dm_list_v1(token):
    '''
    Returns the list of DMs that the user is a member of
    
    Arguments:
        token (str) - session token for the logged in user 

    Exceptions:
        AccessError occurs when:
            - The token is not valid

    Returns:
        - Lists of dictionaries, where each dictionary contains the correspondings DM's name and dm_id
    '''

    auth_user_id = check_session_id(token)

    list_of_dms = []

    for dm in dms:
        for member in dm['all_members']:
            if member['u_id'] == auth_user_id:
                list_of_dms.append({'dm_id': dm['id'], 'name': dm['name']})

    return {
        "dms": list_of_dms
    }


def dm_invite_v1(token, dm_id, u_id):
    '''
    Inviting a user to an existing DM
    Arguments:
        token (str) - session token for the logged in user inviting another user
        dm_id (int) - ID of the DM
        u_id (int) - ID of the user that is being invited
    Exceptions:
        InputError when:
        - dm_id does not refer to a valid DM
        - u_id does not refer to a valid user.
        AccessError when:
        - the authorised user is not already a member of the DM
        - The token is not valid
    Returns:
        - an empty dictionary
    '''

    auth_user_id = check_session_id(token)

    if not isinstance(dm_id, int):
        raise InputError(description='dm_id has to be an integer')

    user_found = False
    for user in users:
        # the user is counted as invalid if they have been removed from Dreams
        if user['u_id'] == u_id and not (user["name_first"] == "Removed" and 
                                         user["name_last"] == "user"):
            user_found = True

    # Not a valid user
    if user_found == False:
        raise InputError(description=f"{u_id} is not a valid user ID")

    auth_user_found = False
    invalid_dm = True
    for dm in dms:
        for member in dm['all_members']:
            if member['u_id'] == auth_user_id:
                auth_user_found = True
        if dm['id'] == dm_id:
            invalid_dm = False
    
    # Not a valid dm
    if invalid_dm == True:
        raise InputError(description="DM id is invalid")

    # Authorised user is not already a member of the dm
    if auth_user_found == False:
        raise AccessError(description="The authorised user is not a member of the DM")

    # Find the details of the user
    for user in users:
        if user['u_id'] == u_id:
            name_first = user['name_first']
            name_last = user['name_last']
            email = user['email']
            handle = user['handle_str']

    for dm in dms:
        if dm['id'] == dm_id:
            # Function does nothing if the user is already a member of the dm
            for member in dm['all_members']:
                if member['u_id'] == u_id:
                    return {
                    }

            dm['all_members'].append(
                {
                'u_id': u_id,
                'email': email,
                'name_first': name_first,
                'name_last': name_last,
                'handle_str': handle,
                },
            )
    notifications_added(dm_id, auth_user_id, [u_id], False)
    
    update_data_write()
    return {
    }

def dm_messages_v1(token, dm_id, start):
    '''
    Given a DM with ID channel_id that the authorised user is part of, return up to 50 messages 
    between index "start" and "start + 50". Message with index 0 is the most recent message in the dm. 
    This function returns a new index "end" which is the value of "start + 50", or, if this function has 
    returned the least recent messages in the dm, returns -1 in "end" to indicate there are no more 
    messages to load after this return.

    Arguments:
        token :: [str] - session token for the logged in user calling the function
        dm_id :: [int] - the id of the dm whose messages are to be provided
        start :: [int] - the starting index to return the messages from
    Exceptions:
        InputError - occurs when:
            - DM ID is not a valid dm
            - Start is greater than the total number of messages in the dm
        AccessError - occurs when:
            - Authorised user is not a member of dm with dm_id
            - The token is not valid    
    
    Return Value:
        (dict) containing:
            - List of messages
            - Start index
            - Ending index
    '''

    auth_user_id = check_session_id(token)

    this_dm = False
    auth_user_in_channel = False
    end = start + 50
    total_messages = 0
    messages = []
    
    for dm in dms:
        if dm['id'] == dm_id:
            this_dm = dm

    if this_dm == False:
        raise InputError(description='dm_id does not refer to any existing dm')


    for auth_user in this_dm['all_members']:
        if auth_user_id == auth_user['u_id']:
            auth_user_in_channel = True
    
    total_messages = len(this_dm['messages'])
    if start > total_messages:
        raise InputError(description="Start is greater than total number of messages")

    r_messages_list = this_dm['messages'].copy()
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
        raise AccessError(description='Authorised user is not a member of this dm')

    return {
        'messages': messages,
        'start': start,
        'end': end,
    }


def dm_details_v1(token, dm_id):
    """
    Given a DM with ID dm_id that the authorised user is part of, 
    provide basic details about the DM

    Arguments:
        token (str) - session token for the logged in user calling the function
        dm_id (int) - ID of the DM whose details are to be provided

    Exceptions:
        InputError - Occurs when:
            - dm_id is not a valid DM
        AccessError - Occurs when:
            - The token is not a valid id
            - The authorised user is not a member of the DM
    
    Return Value:
        dict (containing):
            - name (name of the DM)
            - members (list of dictionaries where each dictionary contains the respective
              member's u_id, email, name_first, name_last and handle_str)
    """

    auth_user_id = check_session_id(token)

    valid_dm = False
    for dm in dms:
        if dm["id"] == dm_id:
            valid_dm = True
            dm_members = dm["all_members"]
            dm_name = dm["name"]

    if valid_dm == False:
        raise InputError(description="dm_id is not a valid DM")

    is_member = False
    for member in dm_members:
        if member['u_id'] == auth_user_id:
            is_member = True

    if is_member == False:
        raise AccessError(description="Authorised user is not a member of DM with dm_id")

    return {
        "name": dm_name,
        "members": dm_members
    }


def dm_remove_v1(token, dm_id):
    """
    Remove an existing DM from Dreams. This can only be done by the original 
    creator of the DM.

    Arguments:
        token (str) - session token for the logged in user calling the function
        dm_id (int) - ID of the DM which is to be removed

    Exceptions:
        InputError - Occurs when:
            - dm_id is not a valid DM
        AccessError - Occurs when:
            - The token is not a valid id
            - The authorised user is not the original creator of the dm or a global owner

    Return Value:
        {}
    """

    auth_user_id = check_session_id(token)

    valid_dm = False
    for idx, dm in enumerate(dms):
        if dm["id"] == dm_id:
            valid_dm = True
            dm_num = idx
            dm_owners = dm["owner_members"]

    if valid_dm == False:
        raise InputError(description="dm_id is not a valid DM")

    dm_owner = False
    for owner in dm_owners:
        if owner["u_id"] == auth_user_id:
            dm_owner = True

    global_owner = False
    for user in users:
        if user["u_id"] == auth_user_id:
            if user["permission_id"] == 1:
                global_owner = True

    if dm_owner == False and global_owner == False:
        raise AccessError(description="Authorised user is not the creator of DM with dm_id")

    del dms[dm_num]

    update_data_write()
    
    return {}


def dm_leave_v1(token, dm_id):
    """
    Given a DM ID, the authorised user is removed as a member of this DM

    Arguments:
        token (str) - session token for the logged in user calling the function
        dm_id (int) - ID of the DM which the authorised user is leaving

    Exceptions:
        InputError - Occurs when:
            - dm_id is not a valid DM
        AccessError - Occurs when:
            - The token is not a valid id
            - The authorised user is not a member of the DM with dm_id

    Return Value:
        {}
    """

    auth_user_id = check_session_id(token)

    valid_dm = False
    for dm in dms:
        if dm["id"] == dm_id:
            valid_dm = True
            dm_owners = dm["owner_members"]
            dm_members = dm["all_members"]

    if valid_dm == False:
        raise InputError(description="dm_id is not a valid DM")

    is_member = False
    for idx, member in enumerate(dm_members):
        if member['u_id'] == auth_user_id:
            is_member = True
            member_num = idx

    if is_member == False:
        raise AccessError(description="Authorised user is not a member of DM with dm_id")

    dm_owner = False
    for idx, owner in enumerate(dm_owners):
        if owner["u_id"] == auth_user_id:
            dm_owner = True
            owner_num = idx

    del dm_members[member_num]

    if dm_owner == True:
        del dm_owners[owner_num]

    update_data_write()

    return {}
