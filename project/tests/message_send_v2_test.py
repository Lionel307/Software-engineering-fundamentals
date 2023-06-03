import pytest

from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channels import channels_create_v2
from src.message import message_send_v2
from src.channel import channel_messages_v2, channel_join_v2
from src.error import AccessError, InputError
from src.other import clear_v1


@pytest.fixture
def users():
    clear_v1()
    user = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    user_2 = auth_register_v2('anothervalidemail@gmail.com', '123abc!@#', 'Hayden', 'Smith')
    user_3 = auth_register_v2('yetanothervalidemail@gmail.com', '123abc!@#', 'Nothayden', 'Smith')
    users = [user, user_2, user_3]

    return users


@pytest.fixture
def channels(users):
    dict_channel_id = channels_create_v2(users[0]["token"], "user 1's channel", True)
    dict_channel_id2 = channels_create_v2(users[1]["token"], "user 2's channel", True)
    channel_ids = [dict_channel_id['channel_id'], dict_channel_id2['channel_id']]

    return channel_ids

def test_one_message(users, channels):
    message = "hello"
    message_id = message_send_v2(users[0]["token"], channels[0], message)
    message_id = message_id["message_id"]
    assert type(message_id) == int

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)


    assert message_list["messages"][0]["message"] == message
    assert message_list["messages"][0]["message_id"] == message_id
    assert message_list["messages"][0]["u_id"] == users[0]["auth_user_id"]


def test_different_user_one_message(users, channels):
    message = "Programming in Python is fun @mj "

    channel_join_v2(users[1]["token"], channels[0])

    message_id = message_send_v2(users[1]["token"], channels[0], message)
    message_id = message_id["message_id"]

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)


    assert message_list["messages"][0]["message"] == message
    assert message_list["messages"][0]["message_id"] == message_id
    assert message_list["messages"][0]["u_id"] == users[1]["auth_user_id"]


def test_not_a_member(users, channels):
    message = "Programming in Python is fun"

    with pytest.raises(AccessError):
        message_send_v2(users[0]["token"], channels[1], message)

    with pytest.raises(AccessError):
        message_send_v2(users[1]["token"], channels[0], message)

def test_long_message(users, channels):
    message = "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat: it was a hobbit-hole, and that means comfort. It had a perfectly round door like a porthole, painted green, with a shiny yellow brass knob in the exact middle. The door opened on to a tube-shaped hall like a tunnel: a very comfortable tunnel without smoke, with panelled walls, and floors tiled and carpeted, provided with polished chairs, and lots and lots of pegs for hats and coats - the hobbit was fond of visitors. The tunnel wound on and on, going fairly but not quite straight into the side of the hill - The Hill, as all the people for many miles round called it - and many little round doors opened out of it, first on one side and then on another. No going upstairs for the hobbit: bedrooms, bathrooms, cellars, pantries (lots of these), wardrobes (he had whole rooms devoted to clothes), kitchens, dining-rooms, all were on the same floor, and indeed on the same passage. The best rooms were all on the left-hand side (going in), for these were the only ones to have windows, deep-set round windows looking over his garden and meadows beyond, sloping down to the river."

    with pytest.raises(InputError):
        message_send_v2(users[0]["token"], channels[0], message)



def test_invalid_token(users, channels):
    message = "Programming in Python is fun"

    auth_logout_v1(users[0]["token"])
    auth_logout_v1(users[1]["token"])

    with pytest.raises(AccessError):
        message_send_v2(users[0]["token"], channels[0], message)

    with pytest.raises(AccessError):
        message_send_v2(users[1]["token"], channels[1], message)

    with pytest.raises(AccessError):
        message_send_v2("this is a invalid token", channels[0], message)

    with pytest.raises(AccessError):
        message_send_v2(1, channels[0], message)

def test_invalid_channel(users, channels):
    message = "Programming in Python is fun"

    with pytest.raises(InputError):
        message_send_v2(users[0]["token"], 42, message)

    with pytest.raises(InputError):
        message_send_v2(users[0]["token"], -3, message)

    clear_v1()