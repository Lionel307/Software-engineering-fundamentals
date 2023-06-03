import pytest

from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channels import channels_create_v2
from src.message import message_send_v2, message_senddm_v1, message_react_v1, message_unreact_v1
from src.channel import channel_invite_v2, channel_join_v2, channel_messages_v2
from src.dm import dm_invite_v1, dm_create_v1, dm_messages_v1
from src.error import AccessError, InputError
from src.other import clear_v1, notifications_get_v1

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
    dict_dm_id = dm_create_v1(users[0]["token"], [users[1]["auth_user_id"], users[2]["auth_user_id"]])
    return [dict_channel_id['channel_id'], dict_dm_id['dm_id']]

def test_op_user_reacting_and_unreacting(users, channels):
    message = "hello"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]

    message_react_v1(users[0]["token"], message_id, 1)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]

    assert message_list[0]["message_id"] == message_id
    assert users[0]["auth_user_id"] in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["react_id"] == 1
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == True

    message_unreact_v1(users[0]["token"], message_id, 1)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]

    assert message_list[0]["message_id"] == message_id
    assert users[0]["auth_user_id"] not in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["react_id"] == 1
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == False

def test_several_users_reacting_and_notif(users, channels):
    message = "hello"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]
    channel_join_v2(users[1]["token"], channels[0])
    channel_join_v2(users[2]["token"], channels[0])

    message_react_v1(users[0]["token"], message_id, 1)
    message_react_v1(users[1]["token"], message_id, 1)

    notifications = notifications_get_v1(users[0]["token"])["notifications"]

    # User 0 is calling channel_messages
    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)["messages"]
    assert users[0]["auth_user_id"] in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["react_id"] == 1
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == True

    # User 1 is calling channel_messages
    message_list = channel_messages_v2(users[1]["token"], channels[0], 0)["messages"]
    assert users[1]["auth_user_id"] in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == True

    # User 2 is calling channel_messages
    message_list = channel_messages_v2(users[2]["token"], channels[0], 0)["messages"]
    assert users[2]["auth_user_id"] not in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == False

    assert notifications[0]["channel_id"] == channels[0]
    assert notifications[0]["dm_id"] == -1
    assert notifications[0]["notification_message"] == "haydensmith reacted to your message in user 1's channel"

    message_unreact_v1(users[1]["token"], message_id, 1)

    message_list = channel_messages_v2(users[1]["token"], channels[0], 0)["messages"]
    assert users[1]["auth_user_id"] not in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == False

def test_invalid_message_id(users, channels):

    with pytest.raises(InputError):
        message_react_v1(users[0]["token"], 43892798, 1)

    with pytest.raises(InputError):
        message_unreact_v1(users[0]["token"], 43892798, 1)

def test_invalid_react_id(users, channels):
    message = "hello"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]

    with pytest.raises(InputError):
        message_react_v1(users[0]["token"], message_id, 42)

    with pytest.raises(InputError):
        message_unreact_v1(users[0]["token"], message_id, 42)

def test_not_a_memmber(users, channels):
    message = "hello"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]

    with pytest.raises(AccessError):
        message_react_v1(users[1]["token"], message_id, 1)

    with pytest.raises(AccessError):
        message_unreact_v1(users[1]["token"], message_id, 1)

def test_already_reacted_or_unreacted(users, channels):
    message = "hello"
    message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]

    with pytest.raises(InputError):
        message_unreact_v1(users[0]["token"], message_id, 1)

    message_react_v1(users[0]["token"], message_id, 1)

    with pytest.raises(InputError):
        message_react_v1(users[0]["token"], message_id, 1)


def test_op_user_reacting_and_unreacting_in_dm(users, channels):
    message = "hello"
    message_id = message_senddm_v1(users[0]["token"], channels[1], message)["message_id"]

    message_react_v1(users[0]["token"], message_id, 1)

    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]

    assert message_list[0]["message_id"] == message_id
    assert users[0]["auth_user_id"] in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["react_id"] == 1
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == True

    message_unreact_v1(users[0]["token"], message_id, 1)

    message_list = dm_messages_v1(users[0]["token"], channels[1], 0)["messages"]

    assert message_list[0]["message_id"] == message_id
    assert users[0]["auth_user_id"] not in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["react_id"] == 1
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == False

    clear_v1()