import json
import jwt
import time
import uuid
import threading

from .data import users, channels, dms, notifications, sessions, reset_codes
from .error import InputError, AccessError


def clear_v1():
    '''
    Resets the internal data of the application to it's initial state

    Arguments:
        None
    
    Exceptions:
        N/A
    
    Return Value:
        {} - Empty dict
    '''

    users.clear()
    channels.clear()
    dms.clear()
    notifications.clear()
    sessions.clear()
    reset_codes.clear()

    update_data_write()

    return {}


def search_v2(token, query_str):
    '''
    Given a query string, return a collection of messages in all of the 
    channels/DMs that the user has joined that match the query

    Arguments:
        token (str) - session token of logged in user calling the function.
        query_str (str) - the query that will be used to search for matching messages

    Exceptions:
        InputError - Occurs when:
            - query_str is more than 1000 characters
        AccessError - Occurs when:
            - The token is not a valid user

    Returns:
        (dict) containing a list of dictionaries, where each dictionary
        contains the corresponding message's message_id, u_id of user who sent the 
        message, message, time_created
    '''

    auth_user_id = check_session_id(token)

    if len(query_str) > 1000:
        raise InputError(description="Query string cannot be more than 1000 characters")

    # this is going to be a list of all messages from channels and dms that the authorised 
    # user is part of
    list_all_messages = []
    
    for channel in channels:
        for member in channel['all_members']:
            if member['u_id'] == auth_user_id:
                list_all_messages.extend(channel['messages'])

    for dm in dms:
        for member in dm['all_members']:
            if member['u_id'] == auth_user_id:
                list_all_messages.extend(dm['messages'])

    matching_messages = []
    for message in list_all_messages:
        if query_str in message['message']:
            matching_messages.append(message)

    return {'messages': matching_messages}


def notifications_get_v1(token):
    '''
    Return the user's most recent 20 notifications

    Arguments:
        token :: [str] - auth token

    Exceptions:
        AccessError - Occurs when:
            - Token is invalid
            - User is not logged in

    Return Value:
        notifications :: [dict] - List of dictionaries, 
        where each dictionary contains types { channel_id, dm_id, notification_message }

    '''

    temp_notification_list = []
    notification_list = []

    u_id = check_session_id(token)

    for notification in reversed(notifications):
        if notification["target_id"] == u_id:
            temp_notification_list.append(notification)
        if len(temp_notification_list) >= 20:
            break
    
    for notification in temp_notification_list:
        notification_message = ""
        channel_name = notification["channel/dm_name"]
        message = notification["message"]
        sender_handle = notification["sender_handle"]

        if notification["type"] == "tagged":
            notification_message = f"{sender_handle} tagged you in {channel_name}: {message}"

        elif notification["type"] == "added":
            notification_message = f"{sender_handle} added you to {channel_name}"
        
        elif notification["type"] == "reacted":
            notification_message = f"{sender_handle} reacted to your message in {channel_name}"

        notification_list.append({
            "channel_id": notification["channel_id"],
            "dm_id": notification["dm_id"],
            "notification_message": notification_message
        })
    return {
        "notifications": notification_list
    }

def check_session_id(token):
    '''
    Checks if the user is logged in and returns the user id.

    Arguments:
        token :: [str] - auth token

    Exceptions:
        AccessError - Occurs when:
            - Token is invalid
            - User is not logged in

    Return Value:
        u_id :: [int]
    '''

    secret = get_secret()

    # Raises AccessError if the decoding fails due to signature error
    try:
        decoded = jwt.decode(token, secret, algorithms=['HS256'])
    except Exception:
        raise AccessError(description="Invalid token") from Exception


    session_id = decoded["session_id"]

    # Checks if the user is logged in
    logged_in = False
    for item in sessions:
        if item["session_id"] == session_id:
            u_id = item["u_id"]
            logged_in = True

    if logged_in == False:
        raise AccessError(description="Not logged in")


    return u_id


def get_secret():
    '''
    Returns a secret. This secret is static for the moment.

    Arguments:
        None

    Exceptions:
        N/A

    Return Value:
        secret :: [str]
    '''

    secret = "COMP1531_is_fun!!"

    return secret


def update_data_read():
    '''
    Updates the temporary data store with persistent data.

    Arguments:
        None

    Exceptions:
        N/A
    
    Return Value:
        None
    '''

    with open("./src/data.json", "r") as FILE:
        data = json.load(FILE)
    
    channels.clear()
    channels.extend(data["channels"])

    users.clear()
    users.extend(data["users"])

    dms.clear()
    dms.extend(data["dms"])
    
    notifications.clear()
    notifications.extend(data["notifications"])

    reset_codes.clear()
    reset_codes.extend(data["reset_codes"])

def update_data_write():
    '''
    Writes the temporary data to data.json for persistence

    Arguments:
        None

    Exceptions:
        N/A

    Return Value:
        None
    '''

    data = {
    "users": users,

    "channels": channels,

    "dms": dms,

    "notifications": notifications,

    "reset_codes": reset_codes
    }

    with open("./src/data.json", "w") as FILE:
        json.dump(data, FILE)


def check_message_tagging(auth_user_id, message, channel_or_dm_id, is_channel, already_tagged):
    '''
    Checks a message for tags and adds it to the notifications list if it finds a valid tag.

    Arguments:
        auth_user_id :: [int] - u_id for the user sending the message
        message :: [str] - The message sent
        channel_or_dm_id :: [int] - id of the channel or dm the message is being sent in
        is_channel :: [bool] - True if it being sent in a channel, False if being sent in a dm
        already_tagged :: [list] - list of users with u_id already tagged in the message

    Exceptions:
        None

    Return Value:
        None
    '''
    
    index = message.find('@')
    if index == -1:
        return

    tagged_user_handle = False
    for user in users:
        if message.find('@' + user["handle_str"]) != -1 and user["u_id"] not in already_tagged:
            tagged_user_handle = user["handle_str"]
    if tagged_user_handle == False:
        return


    target_id = False
    channel_or_dm_name = False
    sender_handle = False

    if is_channel == True:
        for channel in channels:
            if channel["id"] == channel_or_dm_id:
                this_channel = channel
                channel_or_dm_name = channel["name"]

        for member in this_channel["all_members"]:
            if member["handle_str"] == tagged_user_handle:
                target_id = member["u_id"]
            if member["u_id"] == auth_user_id:
                sender_handle = member["handle_str"]


    if is_channel == False:
        for dm in dms:
            if dm["id"] == channel_or_dm_id:
                this_dm = dm
                channel_or_dm_name = dm["name"]

        for member in this_dm["all_members"]:
            if member["handle_str"] == tagged_user_handle:
                target_id = member["u_id"]
            if member["u_id"] == auth_user_id:
                sender_handle = member["handle_str"]

    if target_id == False or sender_handle == False or channel_or_dm_name == False:
        return

    if is_channel == True:
        dm_id = -1
        channel_id = channel_or_dm_id
    else:
        dm_id = channel_or_dm_id
        channel_id = -1

    notif = {
        "type": "tagged",
        "sender_handle": sender_handle,
        "target_id": target_id,
        "channel_id": channel_id,
        "dm_id": dm_id,
        "channel/dm_name": channel_or_dm_name,
        "message": message[:20]

    }

    notifications.append(notif)

    already_tagged.append(target_id)

    check_message_tagging(auth_user_id, message, channel_or_dm_id, is_channel, already_tagged)


def notifications_added(channel_or_dm_id, auth_user_id, u_ids, is_channel):
    '''
    Adds a notification to the notifications list when a user is added to a channel or dm

    Arguments:
        auth_user_id :: [int] - u_id for the user adding the member
        channel_or_dm_id :: [int] - id of the channel or dm the member is being added to
        u_ids :: [list] - list of users being added to dm or channel
        is_channel :: [bool] - True if it being added to a channel, False if dm

    Exceptions:
        None

    Return Value:
        None
    '''

    if is_channel == True:
        dm_id = -1
        channel_id = channel_or_dm_id
    else:
        dm_id = channel_or_dm_id
        channel_id = -1
    
    for user in users:
        if user["u_id"] == auth_user_id:
            sender_handle = user["handle_str"]
    
    for channel in channels:
        if channel["id"] == channel_id:
            channel_or_dm_name = channel["name"]
    
    for dm in dms:
        if dm["id"] == dm_id:
            channel_or_dm_name = dm["name"]

    for u_id in u_ids:
        notif = {
            "type": "added",
            "sender_handle": sender_handle,
            "target_id": u_id,
            "channel_id": channel_id,
            "dm_id": dm_id,
            "channel/dm_name": channel_or_dm_name,
            "message": ""
        }
        notifications.append(notif)


def standup_start_v1(token, channel_id, length):
    '''
    For a given channel, start the standup period whereby for the next "length" seconds 
    if someone calls "standup_send" with a message, it is buffered during the X second 
    window then at the end of the X second window a message will be added to the message 
    queue in the channel from the user who started the standup. X is an integer that denotes 
    the number of seconds that the standup occurs for.

    Arguments:
        token (str) - session token of logged in user calling the function.
        channel_id (int) - id of the channel where the standup has to be started
        length (int) - the number of seconds that the standup occurs for

    Exceptions:
        InputError - Occurs when:
            - channel_id is not a valid channel
            - an active standup is already running in the channel with channel_id
        AccessError - Occurs when:
            - authorised user is not a member of the channel with channel_id
            - the token is not a valid user

    Returns:
        (dict) with key "time_finish" (what time the standup finishes)
    '''

    auth_user_id = check_session_id(token)

    valid_channel = False
    for channel in channels:
        if channel["id"] == channel_id:
            valid_channel = True
            ch_messages = channel["messages"]
            # mark a running standup in the channel
            ch_standup = channel["standup"][0]
            ch_members = channel["all_members"]

    if valid_channel == False:
        raise InputError(description="Invalid channel_id")

    if ch_standup["is_active"] == True:
        raise InputError(description="A standup is already active in this channel")

    in_channel = False
    for member in ch_members:
        if member["u_id"] == auth_user_id:
            in_channel = True

    if in_channel == False:
        raise AccessError(description="Only members can start a standup in this channel")

    ch_standup["is_active"] = True
    message_id = str(uuid.uuid1().int)
    message_id = int(message_id[:16])
    current_time = int(time.time())
    time_finish = current_time + length
    ch_standup["time_finish"] = time_finish

    new_message = {
        "message_id": message_id,
        "u_id": auth_user_id,
        "message": "",
        "time_created": time_finish,
        "reacts": [],
        "is_pinned": False
    }

    new_thread = threading.Timer(length, finish_standup, args=[
        auth_user_id, channel_id, new_message, ch_messages, ch_standup
    ])
    new_thread.start()

    update_data_write()

    return {"time_finish": time_finish}


def standup_active_v1(token, channel_id):
    '''
    For a given channel, return whether a standup is active in it, and what time the 
    standup finishes. If no standup is active, then time_finish returns None.

    Arguments:
        token (str) - session token of logged in user calling the function.
        channel_id (int) - id of the channel where the standup has to be started

    Exceptions:
        InputError - Occurs when:
            - channel_id is not a valid channel
        AccessError - Occurs when:
            - the token is not a valid user

    Returns:
        (dict) containing key:
            - is_active (bool which indicates if a standup is active in the channel)
            - time_finish (the time at which the standup finishes, None if no standup is running)
    '''
    check_session_id(token)

    valid_channel = False
    for channel in channels:
        if channel["id"] == channel_id:
            valid_channel = True
            standup_info = channel["standup"][0]

    if valid_channel == False:
        raise InputError(description="Invalid channel_id")

    return {
        "is_active": standup_info["is_active"],
        "time_finish": standup_info["time_finish"]
    }


def standup_send_v1(token, channel_id, message):
    '''
    Send a message to get buffered in the standup queue, assuming a standup is 
    currently active in the channel with channel_id.

    Arguments:
        token (str) - session token of logged in user calling the function
        channel_id (int) - id of the channel where the standup is active
        message (str) - the message to be sent

    Exceptions:
        InputError - Occurs when:
            - channel_id is not a valid channel
            - message is more than 1000 characters
            - an active standup is not currently running in the channel with channel_id
      
        AccessError - Occurs when:
            - the token is not a valid user
            - authorised user is not a member of the channel with channel_id

    Returns:
        {}
    '''
    auth_user_id = check_session_id(token)

    valid_channel = False
    for channel in channels:
        if channel["id"] == channel_id:
            valid_channel = True
            standup_info = channel["standup"][0]
            channel_members = channel["all_members"]

    if valid_channel == False:
        raise InputError(description="Invalid channel_id")

    if len(message) > 1000:
        raise InputError(description="Message cannot be more than 1000 characters")

    if standup_info["is_active"] == False:
        raise InputError(description="A standup is not currently active in this channel")

    in_channel = False
    for member in channel_members:
        if member["u_id"] == auth_user_id:
            in_channel = True
            handle = member["handle_str"]

    if in_channel == False:
        raise AccessError(description="Only members can send a message in this channel")

    new_message = f"{handle}: {message}\n"
    standup_info["message"] += new_message

    update_data_write()

    return {}


def finish_standup(auth_user_id, channel_id, message_details, messages, standup):
    '''
    Append all the messages in the standup queue as a whole message in the channel's 
    list of messages and reset the channel's standup dictionary to its initial state

    Arguments:
        auth_user_id (int) - u_id of the user who started the standup
        channel_id (int) - id of the channel where the standup was started
        messages (list) - list of messages of the channel in which the standup was started
        standup (dict) - contains key "active" whose value indicates if a standup is
            running in that channel and key "message" whose value is a string (all the 
            standup messages concatenated into one message)
        message_details (dict) - contains the details of the new message which is to be
            appended to the channel's list of messages (message_id, u_id, time_created etc.)

    Exceptions:
        None

    Return Value:
        None
    '''

    # all the messages in the standup queue concatenated as a single message 
    new_message = standup["message"].rstrip()
    message_details["message"] = new_message

    messages.append(message_details)
    # check if the message contains a user tagging another user
    check_message_tagging(auth_user_id, new_message, channel_id, True, [])

    # set the standup dictionary of the channel to its initial state
    standup["is_active"] = False
    standup["time_finish"] = None
    standup["message"] = ""

    update_data_write()
