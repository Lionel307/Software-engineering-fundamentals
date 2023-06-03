import src.other
from src.data import channels, users, dms, notifications
from src.error import AccessError, InputError
import datetime
import uuid
import threading
import time

def message_remove_v1(token, message_id):
    '''
    Given a message_id for a message, this message is removed from the channel/DM

    Arguments:
        token :: [str] - session token of logged in user calling the function.
        message_id :: [int] - id of the message to be removed

    Exceptions:
        InputError - Occurs when:
            - Message (based on ID) no longer exists
        AccessError - Occurs when none of the following are true:
            - Message with message_id was sent by the authorised user making this request
            - The authorised user is an owner of this channel (if it was sent to a channel) or the **Dreams**

    Return Value:
        {} - empty dict
    '''

    u_id = src.other.check_session_id(token)

    for user in users:
        if user["u_id"] == u_id:
            permission_id = user["permission_id"]

    message_found = False
    for channel in channels:
        if message_found == True:
            break
        is_channel_owner = False

        for owner in channel["owner_members"]:
            if owner["u_id"] == u_id:
                is_channel_owner = True
        index = 0
        for msg in channel["messages"]:
            if msg["message_id"] == message_id:
                if msg["u_id"] != u_id and permission_id != 1 and is_channel_owner == False:
                    raise AccessError(description="Unauthorised user")


                del channel["messages"][index]
                message_found = True
                break
            index = index + 1


    for dm in dms:
        if message_found == True:
            break
        is_channel_owner = False

        for owner in dm["owner_members"]:
            if owner["u_id"] == u_id:
                is_channel_owner = True
        index = 0
        for msg in dm["messages"]:

            if msg["message_id"] == message_id:
                if msg["u_id"] != u_id and permission_id != 1 and is_channel_owner == False:
                    raise AccessError(description="Unauthorised user")

            if msg["message_id"] == message_id:
                del dm["messages"][index]
                message_found = True
                break
            index = index + 1


    if message_found == False:
        raise InputError(description="Message does not exist")

    src.other.update_data_write()
    return {
    }

def message_edit_v2(token, message_id, message):
    '''
    Given a message, update its text with new text. If the new message is an empty string, the message is deleted.

    Arguments:
        token :: [str] - session token of logged in user calling the function.
        message_id :: [int] - id of the message to be edited
        message :: [str] - new message

    Exceptions:
        InputError - Occurs when:
            - Length of message is over 1000 characters
            - message with message_id does not exist or refers to a deleted message
        AccessError - Occurs when none of the following are true:
            - Message with message_id was sent by the authorised user making this request
            - The authorised user is an owner of this channel (if it was sent to a channel) or the **Dreams**

    Return Value:
        {} - empty dict
    '''

    u_id = src.other.check_session_id(token)

    if len(message) > 1000:
        raise InputError(description="Message can not be more than 1000 characters in length")

    for user in users:
        if user["u_id"] == u_id:
            permission_id = user["permission_id"]


    message_found = False
    for channel in channels:

        is_channel_owner = False

        for owner in channel["owner_members"]:
            if owner["u_id"] == u_id:
                is_channel_owner = True
        channel_id = channel["id"]

        for msg in channel["messages"]:
            if msg["message_id"] == message_id:
                if msg["u_id"] != u_id and permission_id != 1 and is_channel_owner == False:
                    raise AccessError(description="Unauthorised user")
                msg["message"] = message
                message_found = True
                src.other.check_message_tagging(u_id, message, channel_id, True, [])

                break
        if message_found == True:
            break


    for dm in dms:
        is_channel_owner = False

        for owner in dm["owner_members"]:
            if owner["u_id"] == u_id:
                is_channel_owner = True
        dm_id = dm["id"]

        for msg in dm["messages"]:
            if msg["message_id"] == message_id:
                if msg["u_id"] != u_id and permission_id != 1 and is_channel_owner == False:
                    raise AccessError(description="Unauthorised user")
                msg["message"] = message
                message_found = True
                src.other.check_message_tagging(u_id, message, dm_id, False, [])
                break
        if message_found == True:
            break

    if message_found == False:
        raise InputError(description="Message does not exist")

    if message == "":
        message_remove_v1(token, message_id)
    

    src.other.update_data_write()
    return {
    }

def message_send_v2(token, channel_id, message):
    '''
    Send a message from authorised_user to the channel specified by channel_id.

    Arguments:
        token :: [str] - session token of logged in user calling the function.
        channel_id :: [int] - id of the channel to send the message to.
        message :: [str] - the message to be sent.

    Exceptions:
        InputError - Occurs when:
            - Message is more than 1000 characters
            - Channel with channel_id does not exist
        AccessError - Occurs when:
            - the authorised user has not joined the channel they are trying to post to
            - token in invalid

    Return Value:
        {message_id} - message id of the sent message
    '''

    u_id = src.other.check_session_id(token)

    if len(message) > 1000:
        raise InputError(description="Message can not be more than 1000 characters in length")
    
    message_id = str(uuid.uuid1().int)
    message_id = int(message_id[:16])


    utc_time = datetime.datetime.now(datetime.timezone.utc)
    time_created = int(utc_time.replace(tzinfo=datetime.timezone.utc).timestamp())
    

    message_dict = {
        "message_id": message_id,
        "u_id": u_id,
        "message": message,
        "time_created": time_created,
        "reacts": [],
        "is_pinned": False
    }

    valid_channel = False
    user_in_channel = False
    for channel in channels:
        if channel["id"] == channel_id:
            valid_channel = True
            for user in channel["all_members"]:
                if user["u_id"] == u_id:
                    user_in_channel = True
            if user_in_channel == False:
                raise AccessError(description="User is not a member of the channel")

            channel["messages"].append(message_dict)
            break

    if valid_channel == False:
        raise InputError(description="Channel does not exist")

    src.other.check_message_tagging(u_id, message, channel_id, True, [])

    src.other.update_data_write()
    return {
        'message_id': message_id,
    }

def message_senddm_v1(token, dm_id, message):
    '''
    Send a message from authorised_user to the DM specified by dm_id.

    Arguments:
        token :: [str] - session token of logged in user calling the function.
        channel_id :: [int] - id of the channel to send the message to.
        message :: [str] - the message to be sent.

    Exceptions:
        InputError - Occurs when:
            - Message is more than 1000 characters
            - DM with dm_id does not exist
        AccessError - Occurs when:
            - the authorised user is not a member of the DM they are trying to post to
            - token in invalid

    Return Value:
        {message_id} - message id of the sent message
    '''

    u_id = src.other.check_session_id(token)

    if len(message) > 1000:
        raise InputError(description="Message can not be more than 1000 characters in length")
    
    message_id = str(uuid.uuid1().int)
    message_id = int(message_id[:16])


    utc_time = datetime.datetime.now(datetime.timezone.utc)
    time_created = int(utc_time.replace(tzinfo=datetime.timezone.utc).timestamp())

    message_dict = {
        "message_id": message_id,
        "u_id": u_id,
        "message": message,
        "time_created": time_created,
        "reacts": [],
        "is_pinned": False
    }

    valid_dm = False
    user_in_dm = False
    for dm in dms:
        if dm["id"] == dm_id:
            valid_dm = True
            for user in dm["all_members"]:
                if user["u_id"] == u_id:
                    user_in_dm = True
            if user_in_dm == False:
                raise AccessError(description="User is not a member of the dm")
            dm["messages"].append(message_dict)

    if valid_dm == False:
        raise InputError(description="dm with dm_id does not exist")

    src.other.check_message_tagging(u_id, message, dm_id, False, [])

    src.other.update_data_write()

    return {
        'message_id': message_id,
    }


def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    Shares a message with message_id to a channel or dm specified by channel_id or dm_id.

    Arguments:
        token :: [str] - session token of logged in user calling the function.
        og_message_id :: [int] - message_id of the message to be shared
        message :: [str] - the new message to be attached to the shared message
        channel_id :: [int] - id of the channel to share the message to. is -1 if the message is to be shared to a dm
        dm_id :: [int] - id of the dm to share the message to. is -1 if the message is to be shared to a channel

    Exceptions:
        InputError - Occurs when:
            - dm or channel does not exist
            - Message is more than 1000 characters
        AccessError - Occurs when:
            - the authorised user is not a member of the channel/DM they are trying to post to
            - token is invalid

    Return Value:
        {shared_message_id} - message id of the new message
    '''

    src.other.check_session_id(token)

    shared_message = ""

    message_found = False
    for channel in channels:
        for msg in channel["messages"]:
            if msg["message_id"] == og_message_id:
                shared_message = msg["message"]
                message_found = True
                break
        if message_found == True:
            break


    for dm in dms:
        for msg in dm["messages"]:
            if msg["message_id"] == og_message_id:
                shared_message = msg["message"]
                message_found = True
        if message_found == True:
            break

    if message_found == False:
        raise InputError(description="Message does not exist")

    new_message = f"{message}:\n  \"\"\n  {shared_message}\n  \"\""

    shared_message_id = -1

    if channel_id == -1:
        shared_message_id = message_senddm_v1(token, dm_id, new_message)["message_id"]
    else:
        shared_message_id = message_send_v2(token, channel_id, new_message)["message_id"]


    src.other.update_data_write()
    return {
        "shared_message_id": shared_message_id
    }


def message_react_v1(token, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, add a "react" to that particular message

    Arguments:
        token :: [str] - session token of logged in user calling the function.
        message_id :: [int] - id of the message user is reacting to
        react_id :: [int] - id of the react

    Exceptions:
        InputError - Occurs when:
            - message_id is not a valid message within a channel or DM that the authorised user has joined.
            - react_id is not a valid React ID. The only valid react ID the frontend has is 1.
            - Message with ID message_id already contains an active React with ID react_id from the authorised user.
        AccessError - Occurs when:
            - The authorised user is not a member of the channel or DM that the message is within.
            - token is invalid

    Return Value:
        {}
    '''

    u_id = src.other.check_session_id(token)

    if react_id != 1:
        raise InputError(description="Invalid react_id")

    user_handle = False
    message_found = False
    for channel in channels:
        is_in_channel = False
        for member in channel["all_members"]:
            if member["u_id"] == u_id:
                is_in_channel = True
                user_handle = member["handle_str"]

        for message in channel["messages"]:
            if message["message_id"] == message_id:
                if is_in_channel == False:
                    raise AccessError(description="User is not a member of the channel containing the message")
                if u_id in message["reacts"]:
                    raise InputError(description="User has already reacted to this message")
                message["reacts"].append(u_id)
                target_user = message["u_id"]
                message_found = True
                channel_id = channel["id"]
                dm_id = -1
                name = channel["name"]
        if message_found == True:
            break

    for dm in dms:
        is_in_channel = False
        for member in dm["all_members"]:
            if member["u_id"] == u_id:
                is_in_channel = True
                user_handle = member["handle_str"]

        for message in dm["messages"]:
            if message["message_id"] == message_id:
                if is_in_channel == False:
                    raise AccessError(description="User is not a member of the channel containing the message")
                if u_id in message["reacts"]:
                    raise InputError(description="User has already reacted to this message")
                message["reacts"].append(u_id)
                target_user = message["u_id"]
                message_found = True
                channel_id = -1
                dm_id = dm["id"]
                name = dm["name"]

        if message_found == True:
            break
    
    if message_found == False:
        raise InputError(description="Message does not exist")

    notification = {
        "type": "reacted",
        "sender_handle": user_handle,
        "target_id": target_user,
        "channel_id": channel_id,
        "dm_id": dm_id,
        "channel/dm_name": name,
        "message": ""

    }

    notifications.append(notification)

    src.other.update_data_write()
    return {
    }

def message_unreact_v1(token, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, remove a "react" to that particular message

    Arguments:
        token :: [str] - session token of logged in user calling the function.
        message_id :: [int] - id of the message user is unreacting to
        react_id :: [int] - id of the react

    Exceptions:
        InputError - Occurs when:
            - message_id is not a valid message within a channel or DM that the authorised user has joined.
            - react_id is not a valid React ID. The only valid react ID the frontend has is 1.
            - Message with ID message_id does not contain an active React with ID react_id from the authorised user.
        AccessError - Occurs when:
            - The authorised user is not a member of the channel or DM that the message is within.
            - token is invalid

    Return Value:
        {}
    '''

    u_id = src.other.check_session_id(token)

    if react_id != 1:
        raise InputError(description="Invalid react_id")

    # Checks for and removes reacts in channel messages
    message_found = False
    for channel in channels:
        is_in_channel = False
        for member in channel["all_members"]:
            if member["u_id"] == u_id:
                is_in_channel = True

        for message in channel["messages"]:
            if message["message_id"] == message_id:
                if is_in_channel == False:
                    raise AccessError(description="User is not a member of the channel containing the message")
                if u_id not in message["reacts"]:
                    raise InputError(description="User does not have an active react for this message")
                message["reacts"].remove(u_id)
                message_found = True
        if message_found == True:
            break

    # Checks for and removes reacts in dm messages
    for dm in dms:
        is_in_channel = False
        for member in dm["all_members"]:
            if member["u_id"] == u_id:
                is_in_channel = True

        for message in dm["messages"]:
            if message["message_id"] == message_id:
                if is_in_channel == False:
                    raise AccessError(description="User is not a member of the channel containing the message")
                if u_id not in message["reacts"]:
                    raise InputError(description="User does not have an active react for this message")
                message["reacts"].remove(u_id)
                message_found = True
        if message_found == True:
            break

    if message_found == False:
        raise InputError(description="Message does not exist")

    src.other.update_data_write()
    return {
    }

def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Send a message from authorised_user to the channel specified by channel_id automatically at a specified time in the future

    Arguments:
        token :: [str] - session token of logged in user calling the function.
        channel_id :: [int] - id of the channel to send the message to
        message :: [str] - the message to be sent
        time_sent :: [int] - unix timestamp for the message to be sent

    Exceptions:
        InputError - Occurs when:
            - Channel ID is not a valid channel
            - Message is more than 1000 characters long
            - time_sent is a time in the past
        AccessError - Occurs when:
            - The authorised user has not joined the channel they are trying to post to
            - Token is invalid

    Return Value:
        {message_id} - message id of the sent message
    '''
    u_id = src.other.check_session_id(token)

    if len(message) > 1000:
        raise InputError(description="Message can not be more than 1000 characters in length")

    current_time = int(time.time())
    # send the message after how many seconds
    send_in_secs = time_sent - current_time
    if send_in_secs < 0:
        raise InputError(description="The specified time is in the past")

    valid_channel = False
    valid_user = False
    for channel in channels:
        if channel_id == channel["id"]:
            valid_channel = True
            ch_messages = channel["messages"]
            for member in channel["all_members"]:
                if member["u_id"] == u_id:
                    valid_user = True

    if valid_channel == False:
        raise InputError(description="channel with channel_id is not a valid channel")

    if valid_user == False:
        raise AccessError(description="User is not a member of the channel with channel_id")

    message_id = str(uuid.uuid1().int)
    message_id = int(message_id[:16])
    new_thread = threading.Timer(send_in_secs, message_sendlater_thread, args=[
        u_id, channel_id, ch_messages, message, time_sent, message_id, True
    ])
    new_thread.start()

    return{
        "message_id": message_id
    }


def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    Send a message from authorised_user to the dm specified by dm_id automatically at a specified time in the future

    Arguments:
        token :: [str] - session token of logged in user calling the function.
        dm_id :: [int] - id of the dm to send the message to
        message :: [str] - the message to be sent
        time_sent :: [int] - unix timestamp for the message to be sent

    Exceptions:
        InputError - Occurs when:
            - dm_id is not a valid dm
            - Message is more than 1000 characters long
            - time_sent is a time in the past
        AccessError - Occurs when:
            - The authorised user has not joined the dm they are trying to post to
            - Token is invalid

    Return Value:
        {message_id} - message id of the sent message
    '''
    u_id = src.other.check_session_id(token)

    if len(message) > 1000:
        raise InputError(description="Message can not be more than 1000 characters in length")

    current_time = int(time.time())
    # send the message after how many seconds
    send_in_secs = time_sent - current_time
    if send_in_secs < 0:
        raise InputError(description="The specified time is in the past")
    
    valid_dm = False
    valid_user = False
    for dm in dms:
        if dm_id == dm["id"]:
            valid_dm = True
            d_messages = dm["messages"]
            for member in dm["all_members"]:
                if member["u_id"] == u_id:
                    valid_user = True

    if valid_dm == False:
        raise InputError(description="dm with dm_id is not a valid dm")

    if valid_user == False:
        raise AccessError(description="User is not a member of the dm with dm_id")
    
    message_id = str(uuid.uuid1().int)
    message_id = int(message_id[:16])
    new_thread = threading.Timer(send_in_secs, message_sendlater_thread, args=[
        u_id, dm_id, d_messages, message, time_sent, message_id, False
    ])
    new_thread.start()

    return{
        "message_id": message_id
    }


def message_sendlater_thread(u_id, channel_or_dm_id, list_of_messages, message, time_sent, message_id, is_channel):
    message_dict = {
        "message_id": message_id,
        "u_id": u_id,
        "message": message,
        "time_created": time_sent,
        "reacts": [],
        "is_pinned": False
    }

    list_of_messages.append(message_dict)

    if is_channel == True:
        src.other.check_message_tagging(u_id, message, channel_or_dm_id, True, [])

    else:
        src.other.check_message_tagging(u_id, message, channel_or_dm_id, False, [])

    src.other.update_data_write()


def message_pin_v1(token, message_id):
    '''
    Given a message within a channel or DM, mark it as "pinned" to be given special display treatment by the frontend

    Arguments:
        token :: [str] - session token of logged in user calling the function.
        message_id :: [int] - id of the message user is pinning

    Exceptions:
        InputError - Occurs when:
            - message_id is not a valid message within a channel or DM that the authorised user has joined.
            - Message with ID message_id already been pinned
        AccessError - Occurs when:
            - The authorised user is not a member of the channel or DM that the message is within.
            - The authorised user is not an owner of the channel or DM
            - token is invalid

    Return Value:
        {}
    '''

    u_id = src.other.check_session_id(token)

    message_found = False

    for channel in channels:
        is_channel_owner = False
        is_in_channel = False
        for member in channel["all_members"]:
            if member["u_id"] == u_id:
                is_in_channel = True
        for member in channel["owner_members"]:
            if member["u_id"] == u_id:
                is_channel_owner = True
                
        for message in channel["messages"]:
            if message["message_id"] == message_id:
                if is_in_channel == False:
                    raise AccessError(description="User is not a member of the channel containing the message")
                if is_in_channel == True and is_channel_owner == False:
                    raise AccessError(description="User is not an owner of the channel containing the message")
                if message["is_pinned"] == True:
                    raise InputError(description="This message has already been pinned")
                message["is_pinned"] = True
                message_found = True

        if message_found == True:
            break

    for dm in dms:
        is_in_channel = False
        for member in dm["all_members"]:
            if member["u_id"] == u_id:
                is_in_channel = True

        for message in dm["messages"]:
            if message["message_id"] == message_id:
                if is_in_channel == False:
                    raise AccessError(description="User is not a member of the channel containing the message")
                if message["is_pinned"] == True:
                    raise InputError(description="This message has already been pinned")
                message["is_pinned"] = True
                message_found = True

        if message_found == True:
            break
    
    if message_found == False:
        raise InputError(description="Message does not exist")

    src.other.update_data_write()
    return {
    }



def message_unpin_v1(token, message_id):
    '''
    Given a message within a channel or DM, remove it's mark as unpinned

    Arguments:
        token :: [str] - session token of logged in user calling the function.
        message_id :: [int] - id of the message user is unreacting to

    Exceptions:
        InputError - Occurs when:
            - message_id is not a valid message within a channel or DM that the authorised user has joined.
            - Message with ID message_id is not pinned
        AccessError - Occurs when:
            - The authorised user is not a member of the channel or DM that the message is within.
            - The authorised user is not an owner of the channel or DM
            - token is invalid

    Return Value:
        {}
    '''

    u_id = src.other.check_session_id(token)
    message_found = False

    for channel in channels:
        is_channel_owner = False
        is_in_channel = False
        for member in channel["all_members"]:
            if member["u_id"] == u_id:
                is_in_channel = True
        for member in channel["owner_members"]:
            if member["u_id"] == u_id:
                is_channel_owner = True
                
        for message in channel["messages"]:
            if message["message_id"] == message_id:
                if is_in_channel == False:
                    raise AccessError(description="User is not a member of the channel containing the message")
                if is_in_channel == True and is_channel_owner == False:
                    raise AccessError(description="User is not an owner of the channel containing the message")
                if message["is_pinned"] == False:
                    raise InputError(description="This message is not pinned")
                message["is_pinned"] = False
                message_found = True

        if message_found == True:
            break

    for dm in dms:
        is_in_channel = False
        for member in dm["all_members"]:
            if member["u_id"] == u_id:
                is_in_channel = True

        for message in dm["messages"]:
            if message["message_id"] == message_id:
                if is_in_channel == False:
                    raise AccessError(description="User is not a member of the channel containing the message")
                if message["is_pinned"] == False:
                    raise InputError(description="This message is not pinned")
                message["is_pinned"] = False
                message_found = True

        if message_found == True:
            break
    if message_found == False:
        raise InputError(description="Message does not exist")

    src.other.update_data_write()
    return {
    }