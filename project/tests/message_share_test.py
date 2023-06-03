import pytest

from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channels import channels_create_v2
from src.message import message_send_v2, message_senddm_v1, message_share_v1
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
    dict_channel_id = channels_create_v2(users[0]["token"], "channel 1", True)
    dict_channel_id_2 = channels_create_v2(users[0]["token"], "channel 2", True)
    dict_dm_id = dm_create_v1(users[0]["token"], [users[1]["auth_user_id"]])
    channel_ids = [dict_channel_id['channel_id'], dict_channel_id_2['channel_id'], dict_dm_id['dm_id']]

    return channel_ids


def test_share_one_message_no_new_message(users, channels):
    message = "Hello"

    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]

    shared_message_id = message_share_v1(users[0]["token"], message_id, "", channels[1], -1)["shared_message_id"]

    message_list = channel_messages_v2(users[0]["token"], channels[1], 0)["messages"]

    assert message_list[0]["message_id"] == shared_message_id
    assert message_list[0]["u_id"] == users[0]["auth_user_id"]

    shared_message_id = message_share_v1(users[0]["token"], message_id, "", -1, channels[2])["shared_message_id"]

    message_list = dm_messages_v1(users[0]["token"], channels[2], 0)["messages"]

    assert message_list[0]["message_id"] == shared_message_id
    assert message_list[0]["u_id"] == users[0]["auth_user_id"]
    assert message_list[0]["message"].find(message) != -1



def test_share_other_user_no_new_message(users, channels):
    message = "Hello"
    channel_join_v2(users[1]["token"], channels[0])
    channel_join_v2(users[1]["token"], channels[1])

    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]

    shared_message_id = message_share_v1(users[1]["token"], message_id, "", channels[1], -1)["shared_message_id"]

    message_list = channel_messages_v2(users[0]["token"], channels[1], 0)["messages"]

    assert message_list[0]["message_id"] == shared_message_id
    assert message_list[0]["u_id"] == users[1]["auth_user_id"]

    shared_message_id = message_share_v1(users[1]["token"], message_id, "", -1, channels[2])["shared_message_id"]

    message_list = dm_messages_v1(users[0]["token"], channels[2], 0)["messages"]

    assert message_list[0]["message_id"] == shared_message_id
    assert message_list[0]["u_id"] == users[1]["auth_user_id"]
    assert message_list[0]["message"].find(message) != -1


def test_share_with_new_message(users, channels):
    message = "Hello"
    new_message = "This is a message"
    channel_join_v2(users[1]["token"], channels[0])
    channel_join_v2(users[1]["token"], channels[1])

    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]

    shared_message_id = message_share_v1(users[1]["token"], message_id, new_message, channels[1], -1)["shared_message_id"]

    message_list = channel_messages_v2(users[0]["token"], channels[1], 0)["messages"]

    assert message_list[0]["message_id"] == shared_message_id
    assert message_list[0]["u_id"] == users[1]["auth_user_id"]
    assert message_list[0]["message"].find(message) != -1
    assert message_list[0]["message"].find(new_message) != -1

    shared_message_id = message_share_v1(users[1]["token"], message_id, new_message, -1, channels[2])["shared_message_id"]

    message_list = dm_messages_v1(users[0]["token"], channels[2], 0)["messages"]

    assert message_list[0]["message_id"] == shared_message_id
    assert message_list[0]["u_id"] == users[1]["auth_user_id"]
    assert message_list[0]["message"].find(message) != -1
    assert message_list[0]["message"].find(new_message) != -1

def test_share_unauthorised(users, channels):
    channel_join_v2(users[1]["token"], channels[0])
    message = "Hello"

    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]

    with pytest.raises(AccessError):
        message_share_v1(users[1]["token"], message_id, "", channels[1], -1)

    with pytest.raises(AccessError):
        message_share_v1(users[2]["token"], message_id, "", channels[1], -1)

    channel_join_v2(users[2]["token"], channels[0])

    with pytest.raises(AccessError):
        message_share_v1(users[2]["token"], message_id, "", -1, channels[2])


def test_one_message_in_dm(users, channels):
    message = "Hello"

    message_id = message_senddm_v1(users[0]["token"], channels[2], message)["message_id"]

    shared_message_id = message_share_v1(users[0]["token"], message_id, "", channels[1], -1)["shared_message_id"]

    message_list = channel_messages_v2(users[0]["token"], channels[1], 0)["messages"]

    assert message_list[0]["message_id"] == shared_message_id
    assert message_list[0]["u_id"] == users[0]["auth_user_id"]

    shared_message_id = message_share_v1(users[0]["token"], message_id, "", -1, channels[2])["shared_message_id"]

    message_list = dm_messages_v1(users[0]["token"], channels[2], 0)["messages"]

    assert message_list[0]["message_id"] == shared_message_id
    assert message_list[0]["u_id"] == users[0]["auth_user_id"]
    assert message_list[0]["message"].find(message) != -1

def test_message_doesnt_exist(users, channels):
    with pytest.raises(InputError):
        message_share_v1(users[0]["token"], 42, "", channels[1], -1)

def test_invalid_token(users, channels):

    message = "Hello"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]

    auth_logout_v1(users[0]["token"])
    with pytest.raises(AccessError):
        message_share_v1(users[0]["token"], message_id, "", channels[1], -1)
    
    with pytest.raises(AccessError):
        message_share_v1("invalid_token", message_id, "", channels[1], -1)

    with pytest.raises(AccessError):
        message_share_v1(42, message_id, "", channels[1], -1)



    clear_v1()