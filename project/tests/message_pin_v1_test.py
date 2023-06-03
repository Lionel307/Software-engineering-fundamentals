import pytest

from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channels import channels_create_v2
from src.message import message_send_v2, message_senddm_v1, message_pin_v1, message_unpin_v1
from src.channel import channel_invite_v2, channel_join_v2, channel_messages_v2
from src.dm import dm_invite_v1, dm_create_v1, dm_messages_v1
from src.error import AccessError, InputError
from src.other import clear_v1, notifications_get_v1

@pytest.fixture
def users():
    clear_v1()
    user = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    user_2 = auth_register_v2('anothervalidemail@gmail.com', '123abc!@#', 'Hayden', 'Smith')
    return [user, user_2]

@pytest.fixture
def channels(users):
    dict_channel_id = channels_create_v2(users[0]["token"], "user 1's channel", True)
    dict_dm_id = dm_create_v1(users[0]["token"], [users[1]["auth_user_id"]])
    return [dict_channel_id['channel_id'], dict_dm_id['dm_id']]

# test if pin and unpin work with one message
def test_user_pinning_and_unpinning(users, channels):
    message = "hello"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]

    message_pin_v1(users[0]["token"], message_id)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]

    assert message_list[0]["message_id"] == message_id
    assert message_list[0]["is_pinned"] == True

    message_unpin_v1(users[0]["token"], message_id)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]

    assert message_list[0]["message_id"] == message_id
    assert message_list[0]["is_pinned"] == False

# test if pin and unpin work with two messages
def test_user_multiple_pinning_and_unpinning(users, channels):
    message_1 = "hello"
    message_2 = "bye"
    message_id_1 = message_send_v2(users[0]["token"], channels[0], message_1)["message_id"]
    message_id_2 = message_send_v2(users[0]["token"], channels[0], message_2)["message_id"]

    message_pin_v1(users[0]["token"], message_id_1)
    message_pin_v1(users[0]["token"], message_id_2)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]

    assert message_list[0]["message_id"] == message_id_2
    assert message_list[0]["is_pinned"] == True
    assert message_list[1]["message_id"] == message_id_1
    assert message_list[1]["is_pinned"] == True

    message_unpin_v1(users[0]["token"], message_id_1)
    message_unpin_v1(users[0]["token"], message_id_2)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]

    assert message_list[0]["message_id"] == message_id_2
    assert message_list[0]["is_pinned"] == False
    assert message_list[1]["message_id"] == message_id_1
    assert message_list[1]["is_pinned"] == False

def test_invalid_message_id(users, channels):

    with pytest.raises(InputError):
        message_pin_v1(users[0]["token"], 43892798)

    with pytest.raises(InputError):
        message_unpin_v1(users[0]["token"], 43892798)

# test if the user pinning or unpinning a message is the owner
def test_user_not_owner(users, channels):
    message = "hello"
    message_id = message_send_v2(users[0]["token"], channels[1], message)["message_id"]

    with pytest.raises(AccessError):
        message_pin_v1(users[1]["token"], message_id)

    message_pin_v1(users[0]["token"], message_id)

    with pytest.raises(AccessError):
        message_unpin_v1(users[1]["token"], message_id)

# test if the user is a member of the channel
def test_not_a_memmber(users, channels):
    message = "hello"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]

    with pytest.raises(AccessError):
        message_pin_v1(users[1]["token"], message_id)

    with pytest.raises(AccessError):
        message_pin_v1(users[1]["token"], message_id)

# test if that the message cant be pinned if already pinned
def test_already_pinned_or_unpinned(users, channels):
    message = "hello"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]

    with pytest.raises(InputError):
        message_unpin_v1(users[0]["token"], message_id)

    message_pin_v1(users[0]["token"], message_id)

    with pytest.raises(InputError):
        message_pin_v1(users[0]["token"], message_id)

# test pin and unpin in dms
def test_user_pinning_and_unpinning_in_dm(users, channels):
    message = "hello"
    message_id = message_senddm_v1(users[0]["token"], channels[1], message)["message_id"]

    message_pin_v1(users[0]["token"], message_id)

    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]

    assert message_list[0]["message_id"] == message_id
    assert message_list[0]["is_pinned"] == True


    message_unpin_v1(users[0]["token"], message_id)

    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]

    assert message_list[0]["message_id"] == message_id
    assert message_list[0]["is_pinned"] == False

    clear_v1()
