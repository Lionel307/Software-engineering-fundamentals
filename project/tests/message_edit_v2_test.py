import pytest

from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channels import channels_create_v2
from src.message import message_send_v2, message_edit_v2, message_senddm_v1
from src.channel import channel_messages_v2, channel_join_v2
from src.error import AccessError, InputError
from src.other import clear_v1
from src.dm import dm_messages_v1, dm_create_v1, dm_invite_v1


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
    dict_dm_id = dm_create_v1(users[0]["token"], [users[1]["auth_user_id"]])
    channel_ids = [dict_channel_id['channel_id'], dict_dm_id['dm_id']]

    return channel_ids


def test_one_message_edited(users, channels):
    og_message = "hello"
    new_message = "Bye"
    message_id = message_send_v2(users[0]["token"], channels[0], og_message)["message_id"]

    message_edit_v2(users[0]["token"], message_id, new_message)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)


    assert message_list["messages"][0]["message"] == new_message
    assert message_list["messages"][0]["message_id"] == message_id
    assert message_list["messages"][0]["u_id"] == users[0]["auth_user_id"]

    message_id = message_senddm_v1(users[0]["token"], channels[1], og_message)["message_id"]
    message_edit_v2(users[0]["token"], message_id, new_message)
    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)

    assert message_list["messages"][0]["message"] == new_message
    assert message_list["messages"][0]["message_id"] == message_id
    assert message_list["messages"][0]["u_id"] == users[0]["auth_user_id"]

def test_many_messages_sent_one_edited(users, channels):
    message_1 = "Hello World!"
    message_2 = "comp1531 is fun!!"

    for _ in range(20):
        message_send_v2(users[0]["token"], channels[0], message_1)
    
    message_id = message_send_v2(users[0]["token"], channels[0], message_2)["message_id"]

    for _ in range(20):
        message_send_v2(users[0]["token"], channels[0], message_1)
    
    message_edit_v2(users[0]["token"], message_id, message_1)
    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]

    for msg in message_list:
        assert msg["message"] == message_1

def test_unauthorised_user(users, channels):
    channel_join_v2(users[1]["token"], channels[0])

    message = "Hello World!"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]
    with pytest.raises(AccessError):
        message_edit_v2(users[1]["token"], message_id, "Hi")
    
    message_id = message_senddm_v1(users[0]["token"], channels[1], message)["message_id"]
    with pytest.raises(AccessError):
        message_edit_v2(users[1]["token"], message_id, "Hi")


def test_channel_owner_edited():
    clear_v1()
    auth_register_v2('eru.iluvatar@gmail.com', '123abc!@#', 'Eru', 'Iluvatar')
    user = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    user_2 = auth_register_v2('anothervalidemail@gmail.com', '123abc!@#', 'Hayden', 'Smith')
    user_3 = auth_register_v2('yetanothervalidemail@gmail.com', '123abc!@#', 'Nothayden', 'Smith')
    users = [user, user_2, user_3]

    dict_channel_id = channels_create_v2(users[0]["token"], "user 1's channel", True)
    dict_dm_id = dm_create_v1(users[0]["token"], [users[1]["auth_user_id"], users[2]["auth_user_id"]])
    channels = [dict_channel_id['channel_id'], dict_dm_id['dm_id']]


    channel_join_v2(users[1]["token"], channels[0])
    channel_join_v2(users[2]["token"], channels[0])

    message = "Hello World!"
    message_1 = "42 is the Answer to the Ultimate Question of Life, the Universe, and Everything"

    message_id_1 = message_send_v2(users[1]["token"], channels[0], message)["message_id"]
    message_id_2 = message_send_v2(users[2]["token"], channels[0], message)["message_id"]

    message_edit_v2(users[0]["token"], message_id_1, message_1)
    message_edit_v2(users[0]["token"], message_id_2, message_1)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]

    for msg in message_list:
        assert msg["message"] == message_1

    message_id_1 = message_senddm_v1(users[1]["token"], channels[0], message)["message_id"]
    message_id_2 = message_senddm_v1(users[2]["token"], channels[0], message)["message_id"]

    message_edit_v2(users[0]["token"], message_id_1, message_1)
    message_edit_v2(users[0]["token"], message_id_2, message_1)

    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]
    for msg in message_list:
        assert msg["message"] == message_1

def test_global_owner():
    clear_v1()
    global_owner = auth_register_v2('eru.iluvatar@gmail.com', '123abc!@#', 'Eru', 'Iluvatar')
    user = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    user_2 = auth_register_v2('anothervalidemail@gmail.com', '123abc!@#', 'Hayden', 'Smith')
    user_3 = auth_register_v2('yetanothervalidemail@gmail.com', '123abc!@#', 'Nothayden', 'Smith')
    users = [user, user_2, user_3]

    dict_channel_id = channels_create_v2(users[0]["token"], "user 1's channel", True)
    dict_dm_id = dm_create_v1(users[0]["token"], [users[1]["auth_user_id"], users[2]["auth_user_id"]])
    channels = [dict_channel_id['channel_id'], dict_dm_id['dm_id']]


    channel_join_v2(users[1]["token"], channels[0])
    channel_join_v2(users[2]["token"], channels[0])

    message = "Hello World!"
    message_1 = "42 is the Answer to the Ultimate Question of Life, the Universe, and Everything"

    message_id_1 = message_send_v2(users[1]["token"], channels[0], message)["message_id"]
    message_id_2 = message_send_v2(users[2]["token"], channels[0], message)["message_id"]

    message_edit_v2(global_owner["token"], message_id_1, message_1)
    message_edit_v2(global_owner["token"], message_id_2, message_1)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]

    for msg in message_list:
        assert msg["message"] == message_1

    message_id_1 = message_senddm_v1(users[1]["token"], channels[0], message)["message_id"]
    message_id_2 = message_senddm_v1(users[2]["token"], channels[0], message)["message_id"]

    message_edit_v2(global_owner["token"], message_id_1, message_1)
    message_edit_v2(global_owner["token"], message_id_2, message_1)

    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]
    for msg in message_list:
        assert msg["message"] == message_1

def test_message_removed(users, channels):
    message = "Hello World!"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]
    message_edit_v2(users[0]["token"], message_id, "")
    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]
    assert len(message_list) == 0

    with pytest.raises(InputError):
        message_edit_v2(users[0]["token"], message_id, "hello")

    message_id = message_senddm_v1(users[0]["token"], channels[1], message)["message_id"]
    message_edit_v2(users[0]["token"], message_id, "")
    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]
    assert len(message_list) == 0

    with pytest.raises(InputError):
        message_edit_v2(users[0]["token"], message_id, "hello")

def test_message_doesnt_exist(users, channels):
    with pytest.raises(InputError):
        message_edit_v2(users[0]["token"], 5, "hello")

def test_long_message(users, channels):
    message_2 = "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat: it was a hobbit-hole, and that means comfort. It had a perfectly round door like a porthole, painted green, with a shiny yellow brass knob in the exact middle. The door opened on to a tube-shaped hall like a tunnel: a very comfortable tunnel without smoke, with panelled walls, and floors tiled and carpeted, provided with polished chairs, and lots and lots of pegs for hats and coats - the hobbit was fond of visitors. The tunnel wound on and on, going fairly but not quite straight into the side of the hill - The Hill, as all the people for many miles round called it - and many little round doors opened out of it, first on one side and then on another. No going upstairs for the hobbit: bedrooms, bathrooms, cellars, pantries (lots of these), wardrobes (he had whole rooms devoted to clothes), kitchens, dining-rooms, all were on the same floor, and indeed on the same passage. The best rooms were all on the left-hand side (going in), for these were the only ones to have windows, deep-set round windows looking over his garden and meadows beyond, sloping down to the river."
    message_id = message_send_v2(users[0]["token"], channels[0], "hello")["message_id"]
    with pytest.raises(InputError):
        message_edit_v2(users[0]["token"], message_id, message_2)

    clear_v1()