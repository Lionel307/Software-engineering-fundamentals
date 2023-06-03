import pytest

from src.auth import auth_register_v2, auth_logout_v1
from src.message import message_send_v2, message_senddm_v1, message_remove_v1
from src.channels import channels_create_v2
from src.channel import channel_join_v2, channel_messages_v2
from src.dm import dm_create_v1, dm_messages_v1
from src.other import clear_v1
from src.error import AccessError, InputError

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

def test_one_message_sent_and_removed(users, channels):
    message = "Hello World!"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]
    message_remove_v1(users[0]["token"], message_id)
    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]
    assert len(message_list) == 0

    message_id = message_senddm_v1(users[0]["token"], channels[1], message)["message_id"]
    message_remove_v1(users[0]["token"], message_id)
    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]
    assert len(message_list) == 0

def test_other_user_one_message(users, channels):
    message = "Hello World!"
    channel_join_v2(users[1]["token"], channels[0])

    message_id = message_send_v2(users[1]["token"], channels[0], message)["message_id"]
    message_remove_v1(users[1]["token"], message_id)
    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]
    assert len(message_list) == 0

    message_id = message_senddm_v1(users[1]["token"], channels[1], message)["message_id"]
    message_remove_v1(users[1]["token"], message_id)
    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]
    assert len(message_list) == 0

def test_more_messages_sent(users, channels):
    message_1 = "Hello World!"
    message_2 = "comp1531 is fun!!"

    for _ in range(20):
        message_send_v2(users[0]["token"], channels[0], message_1)
    
    message_id = message_send_v2(users[0]["token"], channels[0], message_2)["message_id"]

    for _ in range(20):
        message_send_v2(users[0]["token"], channels[0], message_1)
    
    message_remove_v1(users[0]["token"], message_id)
    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]

    is_removed = True
    for msg in message_list:
        if msg["message"] == message_2:
            is_removed = False
    
    assert is_removed == True

    for _ in range(20):
        message_senddm_v1(users[0]["token"], channels[0], message_1)
    
    message_id = message_senddm_v1(users[0]["token"], channels[0], message_2)["message_id"]

    for _ in range(20):
        message_senddm_v1(users[0]["token"], channels[0], message_1)

    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]

    message_remove_v1(users[0]["token"], message_id)
    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]

    for msg in message_list:
        assert msg["message"] == message_1


def test_unauthorised_user(users, channels):
    channel_join_v2(users[1]["token"], channels[0])

    message = "Hello World!"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]
    with pytest.raises(AccessError):
        message_remove_v1(users[1]["token"], message_id)
    
    message_id = message_senddm_v1(users[0]["token"], channels[1], message)["message_id"]
    with pytest.raises(AccessError):
        message_remove_v1(users[1]["token"], message_id)

def test_channel_owner():
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

    message_id_1 = message_send_v2(users[1]["token"], channels[0], message)["message_id"]
    message_id_2 = message_send_v2(users[2]["token"], channels[0], message)["message_id"]

    message_remove_v1(users[0]["token"], message_id_1)
    message_remove_v1(users[0]["token"], message_id_2)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]
    assert len(message_list) == 0

    message_id_1 = message_senddm_v1(users[1]["token"], channels[0], message)["message_id"]
    message_id_2 = message_senddm_v1(users[2]["token"], channels[0], message)["message_id"]

    message_remove_v1(users[0]["token"], message_id_1)
    message_remove_v1(users[0]["token"], message_id_2)

    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]
    assert len(message_list) == 0

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

    message_id_1 = message_send_v2(users[1]["token"], channels[0], message)["message_id"]
    message_id_2 = message_send_v2(users[2]["token"], channels[0], message)["message_id"]

    message_remove_v1(global_owner["token"], message_id_1)
    message_remove_v1(global_owner["token"], message_id_2)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]
    assert len(message_list) == 0

    message_id_1 = message_senddm_v1(users[1]["token"], channels[0], message)["message_id"]
    message_id_2 = message_senddm_v1(users[2]["token"], channels[0], message)["message_id"]

    message_remove_v1(global_owner["token"], message_id_1)
    message_remove_v1(global_owner["token"], message_id_2)

    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]
    assert len(message_list) == 0

def test_message_doesnt_exist(users, channels):
    message = "Hello World!"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]
    message_remove_v1(users[0]["token"], message_id)
    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]
    assert len(message_list) == 0

    with pytest.raises(InputError):
        message_remove_v1(users[0]["token"], message_id)

    message_id = message_senddm_v1(users[0]["token"], channels[1], message)["message_id"]
    message_remove_v1(users[0]["token"], message_id)
    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]
    assert len(message_list) == 0

    with pytest.raises(InputError):
        message_remove_v1(users[0]["token"], message_id)

def test_message_doesnt_exist_2(users, channels):
    with pytest.raises(InputError):
        message_remove_v1(users[0]["token"], 5)

    clear_v1()