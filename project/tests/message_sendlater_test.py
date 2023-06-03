import pytest
import datetime
import time

from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channels import channels_create_v2
from src.message import message_sendlater_v1, message_sendlaterdm_v1
from src.channel import channel_messages_v2, channel_join_v2
from src.dm import dm_create_v1, dm_messages_v1
from src.error import AccessError, InputError
from src.other import clear_v1


@pytest.fixture
def users():
    clear_v1()
    user = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    user_2 = auth_register_v2('anothervalidemail@gmail.com', '123abc!@#', 'Hayden', 'Smith')
    user_3 = auth_register_v2('yetanothervalidemail@gmail.com', '123abc!@#', 'Nothayden', 'Smith')
    return [user, user_2, user_3]

@pytest.fixture
def channels(users):
    dict_channel_id = channels_create_v2(users[0]["token"], "user 1's channel", True)
    dict_dm_id = dm_create_v1(users[0]["token"], [users[1]["auth_user_id"]])
    return [dict_channel_id['channel_id'], dict_dm_id['dm_id']]

def test_channel_and_dm_sendlater_one_message(users, channels):
    message = "Hello There"

    utc_time = datetime.datetime.now(datetime.timezone.utc)
    current_time = int(utc_time.replace(tzinfo=datetime.timezone.utc).timestamp())

    send_time = current_time + 1
    message_id = message_sendlater_v1(users[0]["token"], channels[0], message, send_time)["message_id"]
    message_id_dm = message_sendlaterdm_v1(users[0]["token"], channels[1], message, send_time)["message_id"]

    channel_messages_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]
    dm_messages_list = dm_messages_v1(users[0]["token"], channels[0], 0)["messages"]

    assert len(channel_messages_list) == 0
    assert len(dm_messages_list) == 0

    time.sleep(1.6)

    channel_messages_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]
    dm_messages_list = dm_messages_v1(users[0]["token"], channels[0], 0)["messages"]

    assert channel_messages_list[0]["message"] == message
    assert channel_messages_list[0]["message_id"] == message_id
    assert channel_messages_list[0]["time_created"] == send_time

    assert dm_messages_list[0]["message"] == message
    assert dm_messages_list[0]["message_id"] == message_id_dm
    assert dm_messages_list[0]["time_created"] == send_time

def test_sendlater_many_messages(users, channels):
    message = "Hello There"
    utc_time = datetime.datetime.now(datetime.timezone.utc)
    current_time = int(utc_time.replace(tzinfo=datetime.timezone.utc).timestamp())

    send_time = current_time + 1
    channel_join_v2(users[1]["token"], channels[0])
    msg_id = []
    msg_id_dm = []

    for _ in range(20):
        message_id = message_sendlater_v1(users[1]["token"], channels[0], message, send_time)["message_id"]
        message_id_dm = message_sendlaterdm_v1(users[1]["token"], channels[1], message, send_time)["message_id"]

        msg_id.append(message_id)
        msg_id_dm.append(message_id_dm)
    
    channel_messages_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]
    dm_messages_list = dm_messages_v1(users[0]["token"], channels[0], 0)["messages"]

    assert len(channel_messages_list) == 0
    assert len(dm_messages_list) == 0
    msg_id.reverse()
    msg_id_dm.reverse()
    time.sleep(1.6)

    channel_messages_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]
    dm_messages_list = dm_messages_v1(users[0]["token"], channels[0], 0)["messages"]

    channel_msg_id_list = []
    dm_msg_id_list = []
    for i in range(20):
        channel_msg_id_list.append(channel_messages_list[i]["message_id"])
        dm_msg_id_list.append(dm_messages_list[i]["message_id"])
        assert dm_messages_list[i]["message"] == message
        assert channel_messages_list[i]["message"] == message

    for (c_item, d_item) in zip(msg_id, msg_id_dm):
        assert c_item in channel_msg_id_list
        assert d_item in dm_msg_id_list

def test_long_message(users, channels):
    message = "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat: it was a hobbit-hole, and that means comfort. It had a perfectly round door like a porthole, painted green, with a shiny yellow brass knob in the exact middle. The door opened on to a tube-shaped hall like a tunnel: a very comfortable tunnel without smoke, with panelled walls, and floors tiled and carpeted, provided with polished chairs, and lots and lots of pegs for hats and coats - the hobbit was fond of visitors. The tunnel wound on and on, going fairly but not quite straight into the side of the hill - The Hill, as all the people for many miles round called it - and many little round doors opened out of it, first on one side and then on another. No going upstairs for the hobbit: bedrooms, bathrooms, cellars, pantries (lots of these), wardrobes (he had whole rooms devoted to clothes), kitchens, dining-rooms, all were on the same floor, and indeed on the same passage. The best rooms were all on the left-hand side (going in), for these were the only ones to have windows, deep-set round windows looking over his garden and meadows beyond, sloping down to the river."
    utc_time = datetime.datetime.now(datetime.timezone.utc)
    current_time = int(utc_time.replace(tzinfo=datetime.timezone.utc).timestamp())
    send_time = current_time + 1

    with pytest.raises(InputError):
        message_sendlater_v1(users[0]["token"], channels[0], message, send_time)

    with pytest.raises(InputError):
        message_sendlaterdm_v1(users[0]["token"], channels[1], message, send_time)

def test_not_a_member(users, channels):
    message = "Hello There"

    utc_time = datetime.datetime.now(datetime.timezone.utc)
    current_time = int(utc_time.replace(tzinfo=datetime.timezone.utc).timestamp())
    send_time = current_time + 1

    with pytest.raises(AccessError):
        message_sendlater_v1(users[1]["token"], channels[0], message, send_time)

    with pytest.raises(AccessError):
        message_sendlaterdm_v1(users[2]["token"], channels[1], message, send_time)

def test_invalid_channel(users, channels):
    message = "Hello There"

    utc_time = datetime.datetime.now(datetime.timezone.utc)
    current_time = int(utc_time.replace(tzinfo=datetime.timezone.utc).timestamp())
    send_time = current_time + 1

    with pytest.raises(InputError):
        message_sendlater_v1(users[0]["token"], 42, message, send_time)

    with pytest.raises(InputError):
        message_sendlaterdm_v1(users[0]["token"], 42, message, send_time)

def test_time_sent_in_past(users, channels):
    message = "Hello There"

    utc_time = datetime.datetime.now(datetime.timezone.utc)
    current_time = int(utc_time.replace(tzinfo=datetime.timezone.utc).timestamp())
    send_time = current_time - 5

    with pytest.raises(InputError):
        message_sendlater_v1(users[0]["token"], channels[0], message, send_time)

    with pytest.raises(InputError):
        message_sendlaterdm_v1(users[0]["token"], channels[1], message, send_time)


    clear_v1()