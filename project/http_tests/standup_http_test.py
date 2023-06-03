import pytest
import requests
import json
import time

from src.config import url


def make_request(method, route, data=None):
    '''
    A helper function which makes requests using the given method, route and data
    and returns the response's json object or its status code if an error was raised
    '''
    if method == "POST":
        resp = requests.post(url + route, json=data)
    elif method == "GET":
        resp = requests.get(url + route, params=data)
    elif method == "PUT":
        resp = requests.put(url + route, json=data)
    elif method == "DELETE":
        resp = requests.delete(url + route, json=data)
    else:
        print("Please enter the correct route method")

    if resp.status_code == 400:
        return resp
    elif resp.status_code == 403:
        return resp

    return resp.json()


@pytest.fixture
def users():
    '''
    Creates users for use in tests
    '''
    make_request("DELETE", "clear/v1")

    ROUTE = "auth/register/v2"
    METHOD = "POST"

    user_1 = make_request(METHOD, ROUTE, {
        "email": "email1@gmail.com", "password": "a123!$%", "name_first": "Mark", "name_last": "R"
    })
    user_2 = make_request(METHOD, ROUTE, {
        "email": "email2@gmail.com", "password": "a123!$%", "name_first": "Hayden", "name_last": "S"
    })
    user_3 = make_request(METHOD, ROUTE, {
        "email": "email3@gmail.com", "password": "a123!$%", "name_first": "Mark", "name_last": "R"
    })

    list_users = [user_1, user_2, user_3]

    return list_users


@pytest.fixture
def channel_id_1(users):
    '''
    Creates a channel for use in tests
    '''
    METHOD = "POST"

    channel_1 = make_request(METHOD, "channels/create/v2", {
        "token": users[0]["token"], "name": "channel 1", "is_public": True
    })
    ch_id = channel_1["channel_id"]

    make_request(METHOD, "channel/join/v2", {
        "token": users[1]["token"], "channel_id": ch_id
    })
    make_request(METHOD, "channel/join/v2", {
        "token": users[2]["token"], "channel_id": ch_id
    })

    return ch_id


@pytest.fixture
def start_standup(users, channel_id_1):
    '''
    Starts a standup in channel 1 for use in tests
    '''
    started_standup = make_request("POST", "standup/start/v1", {
        "token": users[0]["token"], "channel_id": channel_id_1, "length": 10
    })

    return started_standup


'''
Tests for standup/start/v1
'''


def test_success_standup_start(users, channel_id_1):
    '''
    A test which checks the output of route standup/start/v1 to see if it is correct
    '''
    LENGTH = 5
    current_time = int(time.time())
    # what time_finish key should be close to (within +2 seconds)
    expected_time_finish = current_time + LENGTH
    expected_time_range = range(expected_time_finish, expected_time_finish + 3)

    started_standup = make_request("POST", "standup/start/v1", {
        "token": users[0]["token"], "channel_id": channel_id_1, "length": LENGTH
    })
    time_stamp = started_standup["time_finish"]

    assert time_stamp in expected_time_range


def test_standup_start_invalid_channel(users):
    '''
    A test which checks if status code 400 is returned when channel_id is not a 
    valid channel
    '''
    LENGTH = 10
    TOKEN = users[0]["token"]
    INPUT_ERROR = 400
    METHOD = "POST"
    ROUTE = "standup/start/v1"

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN, "channel_id": 1, "length": LENGTH
    }).status_code == INPUT_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN, "channel_id": 2, "length": LENGTH
    }).status_code == INPUT_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN, "channel_id": 3, "length": LENGTH
    }).status_code == INPUT_ERROR


def test_standup_start_standup_already_active(users, channel_id_1, start_standup):
    '''
    A test which checks if status code 400 is returned when an active standup is
    currently running in the channel with channel_id
    '''
    LENGTH = 10
    INPUT_ERROR = 400
    METHOD = "POST"
    ROUTE = "standup/start/v1"

    assert make_request(METHOD, ROUTE, {
        "token": users[0]["token"], "channel_id": channel_id_1, "length": LENGTH
    }).status_code == INPUT_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": users[1]["token"], "channel_id": channel_id_1, "length": LENGTH
    }).status_code == INPUT_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": users[2]["token"], "channel_id": channel_id_1, "length": LENGTH
    }).status_code == INPUT_ERROR


def test_standup_start_user_not_member(users, channel_id_1):
    '''
    A test which checks if status code 403 is returned when the authorised user
    is not a member of the channel with channel_id
    '''
    LENGTH = 10
    ACCESS_ERROR = 403
    TOKEN_2 = users[1]["token"]
    TOKEN_3 = users[2]["token"]
    METHOD = "POST"
    ROUTE = "standup/start/v1"

    # user 2 and 3 leave channel 1
    make_request(METHOD, "channel/leave/v1", {
        "token": TOKEN_2, "channel_id": channel_id_1
    })
    make_request(METHOD, "channel/leave/v1", {
        "token": TOKEN_3, "channel_id": channel_id_1
    })

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN_2, "channel_id": channel_id_1, "length": LENGTH
    }).status_code == ACCESS_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN_3, "channel_id": channel_id_1, "length": LENGTH
    }).status_code == ACCESS_ERROR


def test_standup_start_invalid_token(channel_id_1):
    '''
    A test which checks if status code 403 is returned when the token passed in
    is not a valid id
    '''
    LENGTH = 10
    ACCESS_ERROR = 403
    METHOD = "POST"
    ROUTE = "standup/start/v1"

    assert make_request(METHOD, ROUTE, {
        "token": " ", "channel_id": channel_id_1, "length": LENGTH
    }).status_code == ACCESS_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": "invalid token", "channel_id": channel_id_1, "length": LENGTH
    }).status_code == ACCESS_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": 1, "channel_id": channel_id_1, "length": LENGTH
    }).status_code == ACCESS_ERROR


'''
Tests for standup/active/v1
'''


def test_standup_active_success_standup_is_active(users, channel_id_1, start_standup):
    '''
    A test which checks if the return values of the route are correct when a standup
    is running in channel with channel_id
    '''
    standup_status = make_request("GET", "standup/active/v1", {
        "token": users[1]["token"], "channel_id": channel_id_1
    })

    assert standup_status["is_active"] == True
    assert standup_status["time_finish"] == start_standup["time_finish"]


def test_standup_active_success_standup_not_active(users, channel_id_1):
    '''
    A test which checks if the return values of the route are correct when a standup
    is not active in channel with channel_id
    '''
    standup_status = make_request("GET", "standup/active/v1", {
        "token": users[1]["token"], "channel_id": channel_id_1
    })

    assert standup_status["is_active"] == False and standup_status["time_finish"] is None


def test_standup_active_invalid_channel(users):
    '''
    A test which checks if status code 400 is returned when channel_id is not a 
    valid channel
    '''
    TOKEN = users[0]["token"]
    INPUT_ERROR = 400
    METHOD = "GET"
    ROUTE = "standup/active/v1"

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN, "channel_id": 1
    }).status_code == INPUT_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN, "channel_id": 2
    }).status_code == INPUT_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN, "channel_id": 3
    }).status_code == INPUT_ERROR


def test_standup_active_invalid_token(channel_id_1):
    '''
    A test which checks if an AccessError is raised when the token passed in
    is not a valid id
    '''
    ACCESS_ERROR = 403
    METHOD = "GET"
    ROUTE = "standup/active/v1"

    assert make_request(METHOD, ROUTE, {
        "token": " ", "channel_id": channel_id_1
    }).status_code == ACCESS_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": "invalid token", "channel_id": channel_id_1
    }).status_code == ACCESS_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": 1, "channel_id": channel_id_1
    }).status_code == ACCESS_ERROR


'''
Tests for standup/send/v1
'''


def test_standup_send_success(users, channel_id_1, start_standup):
    '''
    A test which checks if all messages sent via standup/send/v1 were successfully added 
    to the standup queue
    '''
    METHOD = "POST"
    ROUTE = "standup/send/v1"

    make_request(METHOD, ROUTE, {
        "token": users[2]["token"], "channel_id": channel_id_1, "message": "hi"
    })
    make_request(METHOD, ROUTE, {
        "token": users[0]["token"], "channel_id": channel_id_1, "message": "Hey tony"
    })
    make_request(METHOD, ROUTE, {
        "token": users[1]["token"], "channel_id": channel_id_1, "message": "Hello World"
    })
    make_request(METHOD, ROUTE, {
        "token": users[1]["token"], "channel_id": channel_id_1, "message": "How is everyone?"
    })
    make_request(METHOD, ROUTE, {
        "token": users[0]["token"], "channel_id": channel_id_1, "message": "I'm in spain but without the s"
    })
    make_request(METHOD, ROUTE, {
        "token": users[2]["token"], "channel_id": channel_id_1, "message": "okay"
    })

    time.sleep(11)

    expected_message = (
        "markr0: hi\n"
        "markr: Hey tony\n"
        "haydens: Hello World\n"
        "haydens: How is everyone?\n"
        "markr: I'm in spain but without the s\n"
        "markr0: okay"
    )
    
    ch_messages = make_request("GET", "channel/messages/v2", {
        "token": users[1]["token"], "channel_id": channel_id_1, "start": 0
    })
    messages = ch_messages["messages"]
    message_1 = messages[0]

    assert message_1["u_id"] == users[0]["auth_user_id"]
    assert message_1["time_created"] == start_standup["time_finish"]
    assert message_1["message"] == expected_message


def test_standup_send_invalid_channel(users):
    '''
    A test which checks if status code 400 is returned when channel_id is not a 
    valid channel
    '''
    MESSAGE = "a message which is irrelevant"
    TOKEN = users[0]["token"]
    INPUT_ERROR = 400
    METHOD = "POST"
    ROUTE = "standup/send/v1"

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN, "channel_id": 1, "message": MESSAGE
    }).status_code == INPUT_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN, "channel_id": 2, "message": MESSAGE
    }).status_code == INPUT_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN, "channel_id": 3, "message": MESSAGE
    }).status_code == INPUT_ERROR


def test_standup_send_invalid_message(users, channel_id_1, start_standup):
    '''
    A test which checks if status code 400 is returned when the message is more 
    than 1000 characters
    '''
    INPUT_ERROR = 400
    LONG_MESSAGE = (
        "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, "
        "with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing "
        "in it to sit down on or to eat: it was a hobbit-hole, and that means comfort. It had a "
        "perfectly round door like a porthole, painted green, with a shiny yellow brass knob in " 
        "the exact middle. The door opened on to a tube-shaped hall like a tunnel: a very "
        "comfortable tunnel without smoke, with panelled walls, and floors tiled and carpeted, "
        "provided with polished chairs, and lots and lots of pegs for hats and coats - the "
        "hobbit was fond of visitors. The tunnel wound on and on, going fairly but not quite "
        "straight into the side of the hill - The Hill, as all the people for many miles round "
        "called it - and many little round doors opened out of it, first on one side and then "
        "on another. No going upstairs for the hobbit: bedrooms, bathrooms, cellars, "
        "pantries (lots of these), wardrobes (he had whole rooms devoted to clothes), kitchens, "
        "dining-rooms, all were on the same floor, and indeed on the same passage. The best rooms "
        "were all on the left-hand side (going in), for these were the only ones to have windows, "
        "deep-set round windows looking over his garden and meadows beyond, sloping down to the "
        "river."
    )

    assert make_request("POST", "standup/send/v1", {
        "token": users[0]["token"], "channel_id": channel_id_1, "message": LONG_MESSAGE
    }).status_code == INPUT_ERROR


def test_standup_send_standup_not_active(users, channel_id_1):
    '''
    A test which checks if status code 400 is returned when there is no standup running
    in the channel with channel_id
    '''
    MESSAGE = "a message which is irrelevant"
    INPUT_ERROR = 400
    METHOD = "POST"
    ROUTE = "standup/send/v1"

    assert make_request(METHOD, ROUTE, {
        "token": users[0]["token"], "channel_id": channel_id_1, "message": MESSAGE
    }).status_code == INPUT_ERROR
    
    assert make_request(METHOD, ROUTE, {
        "token": users[1]["token"], "channel_id": channel_id_1, "message": MESSAGE
    }).status_code == INPUT_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": users[2]["token"], "channel_id": channel_id_1, "message": MESSAGE
    }).status_code == INPUT_ERROR


def test_standup_send_user_not_member(users, channel_id_1, start_standup):
    '''
    A test which checks if status code 403 is returned when the authorised user
    is not a member of the channel with channel_id
    '''
    METHOD = "POST"
    ROUTE = "standup/send/v1"
    ACCESS_ERROR = 403

    user_4 = make_request(METHOD, "auth/register/v2", {
        "email": "email4@gmail.com", "password": "a123!$%", "name_first": "User", "name_last": "4"
    })
    TOKEN = user_4["token"]

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN, "channel_id": channel_id_1, "message": "message 1"
    }).status_code == ACCESS_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN, "channel_id": channel_id_1, "message": "message 2"
    }).status_code == ACCESS_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": TOKEN, "channel_id": channel_id_1, "message": "message 3"
    }).status_code == ACCESS_ERROR


def test_standup_send_invalid_token(channel_id_1, start_standup):
    '''
    A test which checks if status code 403 is returned when the token passed in
    is not a valid id
    '''
    MESSAGE = "a message which is irrelevant"
    ACCESS_ERROR = 403
    METHOD = "POST"
    ROUTE = "standup/send/v1"

    assert make_request(METHOD, ROUTE, {
        "token": "invalid token", "channel_id": channel_id_1, "message": MESSAGE
    }).status_code == ACCESS_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": " ", "channel_id": channel_id_1, "message": MESSAGE
    }).status_code == ACCESS_ERROR

    assert make_request(METHOD, ROUTE, {
        "token": 1, "channel_id": channel_id_1, "message": MESSAGE
    }).status_code == ACCESS_ERROR

    make_request("DELETE", "clear/v1")
