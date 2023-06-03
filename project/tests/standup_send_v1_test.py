import pytest
import time

from src.other import standup_start_v1, standup_send_v1, clear_v1
from src.auth import auth_register_v2
from src.channel import channel_join_v2, channel_messages_v2
from src.channels import channels_create_v2
from src.error import InputError, AccessError


@pytest.fixture
def users():
    '''
    Creates users for use in tests
    '''
    clear_v1()

    user_1 = auth_register_v2("email1@gmail.com", "a123!$%", "Mark", "R")
    user_2 = auth_register_v2("email2@gmail.com", "a123!$%", "Hayden", "S")
    user_3 = auth_register_v2("email3@gmail.com", "a123!$%", "Mark", "R")

    list_users = [user_1, user_2, user_3]

    return list_users


@pytest.fixture
def channel_id_1(users):
    '''
    Creates a channel for use in tests
    '''
    channel_1 = channels_create_v2(users[0]["token"], "channel 1", True)
    ch_id = channel_1["channel_id"]

    channel_join_v2(users[1]["token"], ch_id)
    channel_join_v2(users[2]["token"], ch_id)

    return ch_id


@pytest.fixture
def start_standup(users, channel_id_1):
    '''
    Starts a standup in channel 1 for use in tests
    '''
    started_standup = standup_start_v1(users[0]["token"], channel_id_1, 5)

    return started_standup


def test_success_single_message(users, channel_id_1, start_standup):
    '''
    A test which checks if standup_send_v1 successfuly added a message to the standup
    queue
    '''
    MESSAGE = "Hello there"
    standup_send_v1(users[1]['token'], channel_id_1, MESSAGE)

    time.sleep(5)

    expected_message = f"haydens: {MESSAGE}"
    ch_messages = channel_messages_v2(users[2]["token"], channel_id_1, 0)
    messages = ch_messages["messages"]
    message_1 = messages[0]

    assert message_1["u_id"] == users[0]["auth_user_id"]
    assert message_1["time_created"] == start_standup["time_finish"]
    assert message_1["message"] == expected_message


def test_success_multiple_messages(users, channel_id_1, start_standup):
    '''
    A test which checks if all messages sent via standup_send_v1 were successfully added 
    to the standup queue
    '''
    standup_send_v1(users[2]['token'], channel_id_1, "hi")
    standup_send_v1(users[0]['token'], channel_id_1, "Hey tony")
    standup_send_v1(users[1]['token'], channel_id_1, "Hello World")
    standup_send_v1(users[1]['token'], channel_id_1, "How is everyone?")
    standup_send_v1(users[0]['token'], channel_id_1, "I'm in spain but without the s")
    standup_send_v1(users[2]['token'], channel_id_1, "okay")

    time.sleep(11)

    expected_message = (
        "markr0: hi\n"
        "markr: Hey tony\n"
        "haydens: Hello World\n"
        "haydens: How is everyone?\n"
        "markr: I'm in spain but without the s\n"
        "markr0: okay"
    )
    
    ch_messages = channel_messages_v2(users[1]["token"], channel_id_1, 0)
    messages = ch_messages["messages"]
    message_1 = messages[0]

    assert message_1["u_id"] == users[0]["auth_user_id"]
    assert message_1["time_created"] == start_standup["time_finish"]
    assert message_1["message"] == expected_message


def test_invalid_channel(users):
    '''
    A test which checks if an InputError is raised when channel_id is not a 
    valid channel
    '''
    MESSAGE = "a message which is irrelevant"
    TOKEN = users[0]["token"]

    with pytest.raises(InputError):
        standup_send_v1(TOKEN, 1, MESSAGE)

    with pytest.raises(InputError):
        standup_send_v1(TOKEN, 2, MESSAGE)

    with pytest.raises(InputError):
        standup_send_v1(TOKEN, 3, MESSAGE)


def test_invalid_message(users, channel_id_1, start_standup):
    '''
    A test which checks if an InputError is raised when the message is more than 1000 characters
    '''
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

    with pytest.raises(InputError):
        standup_send_v1(users[0]['token'], channel_id_1, LONG_MESSAGE)


def test_standup_not_active(users, channel_id_1):
    '''
    A test which checks if an InputError is raised when there is no standup running
    in the channel with channel_id
    '''
    MESSAGE = "a message which is irrelevant"

    with pytest.raises(InputError):
        standup_send_v1(users[0]['token'], channel_id_1, MESSAGE)

    with pytest.raises(InputError):
        standup_send_v1(users[1]['token'], channel_id_1, MESSAGE)

    with pytest.raises(InputError):
        standup_send_v1(users[2]['token'], channel_id_1, MESSAGE)


def test_user_not_member(users, channel_id_1, start_standup):
    '''
    A test which checks if an AccessError is raised when the authorised user
    is not a member of the channel with channel_id
    '''
    user_4 = auth_register_v2("email4@gmail.com", "a123!$%", "user", "4")    
    TOKEN = user_4["token"]

    with pytest.raises(AccessError):
        standup_send_v1(TOKEN, channel_id_1, "message 1")

    with pytest.raises(AccessError):
        standup_send_v1(TOKEN, channel_id_1, "message 2")

    with pytest.raises(AccessError):
        standup_send_v1(TOKEN, channel_id_1, "message 3")


def test_invalid_token(channel_id_1, start_standup):
    '''
    A test which checks if an AccessError is raised when the token passed in
    is not a valid id
    '''
    MESSAGE = "a message which is irrelevant"

    with pytest.raises(AccessError):
        standup_send_v1("invalid token", channel_id_1, MESSAGE)

    with pytest.raises(AccessError):
        standup_send_v1(" ", channel_id_1, MESSAGE)

    with pytest.raises(AccessError):
        standup_send_v1(1, channel_id_1, MESSAGE)

    clear_v1()
