import pytest

from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channels import channels_create_v2
from src.message import message_send_v2, message_senddm_v1
from src.channel import channel_invite_v2, channel_join_v2
from src.dm import dm_invite_v1, dm_create_v1
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


def test_one_tag_message_send(users, channels):
    channel_invite_v2(users[0]["token"], channels[0], users[1]["auth_user_id"])

    message_send_v2(users[0]["token"], channels[0], "@haydensmith hi")

    notifications = notifications_get_v1(users[1]["token"])["notifications"]

    # print(notifications)
    assert notifications[0]["notification_message"] == "mj tagged you in user 1's channel: @haydensmith hi"
    assert notifications[0]["channel_id"] == channels[0]
    assert notifications[0]["dm_id"] == -1

    assert notifications[1]["notification_message"] == "mj added you to user 1's channel"
    assert notifications[1]["channel_id"] == channels[0]
    assert notifications[1]["dm_id"] == -1
    

def test_several_users_tagged_message_send(users, channels):
    channel_invite_v2(users[0]["token"], channels[0], users[1]["auth_user_id"])
    channel_invite_v2(users[0]["token"], channels[0], users[2]["auth_user_id"])

    message = "Welcome to my channel @haydensmith and @nothaydensmith"

    message_send_v2(users[0]["token"], channels[0], message)

    cut_message = message[:20]

    notifications_1 = notifications_get_v1(users[1]["token"])["notifications"]
    notifications_2 = notifications_get_v1(users[2]["token"])["notifications"]

    notification_message = f"mj tagged you in user 1's channel: {cut_message}"

    assert notifications_1[0]["notification_message"] == notification_message
    assert notifications_1[0]["channel_id"] == channels[0]
    assert notifications_1[0]["dm_id"] == -1

    assert notifications_1[1]["notification_message"] == "mj added you to user 1's channel"
    assert notifications_1[1]["channel_id"] == channels[0]
    assert notifications_1[1]["dm_id"] == -1


    assert notifications_2[0]["notification_message"] == notification_message
    assert notifications_2[0]["channel_id"] == channels[0]
    assert notifications_2[0]["dm_id"] == -1
    

    assert notifications_2[1]["notification_message"] == "mj added you to user 1's channel"
    assert notifications_2[1]["channel_id"] == channels[0]
    assert notifications_2[1]["dm_id"] == -1

def test_multiple_notifications(users, channels):
    channel_invite_v2(users[0]["token"], channels[0], users[1]["auth_user_id"])
    channel_invite_v2(users[0]["token"], channels[0], users[2]["auth_user_id"])

    message = "Welcome to my channel @haydensmith and @nothaydensmith"
    message_2 = "JK, @nothaydensmith is not welcome here in the slightest"

    for _ in range(25):
        message_send_v2(users[0]["token"], channels[0], message)
        message_send_v2(users[0]["token"], channels[0], message_2)

    cut_message = message[:20]
    cut_message_2 = message_2[:20]

    notifications_1 = notifications_get_v1(users[1]["token"])["notifications"]
    notifications_2 = notifications_get_v1(users[2]["token"])["notifications"]

    notification_message_1 = f"mj tagged you in user 1's channel: {cut_message}"
    notification_message_2 = f"mj tagged you in user 1's channel: {cut_message_2}"

    assert len(notifications_1) == 20
    for i in range(20):
        assert notifications_1[i]["notification_message"] == notification_message_1
        assert notifications_1[i]["channel_id"] == channels[0]
        assert notifications_1[i]["dm_id"] == -1

    for i in range(20):

        if i % 2 == 0:
            assert notifications_2[i]["notification_message"] == notification_message_2
        else:
            assert notifications_2[i]["notification_message"] == notification_message_1


def test_user_not_a_member():
    clear_v1()
    message = "Welcome to my channel @haydensmith and @nothaydensmith"
    user = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    user_2 = auth_register_v2('anothervalidemail@gmail.com', '123abc!@#', 'Hayden', 'Smith')
    dict_channel_id = channels_create_v2(user["token"], "user 1's channel", True)
    message_send_v2(user["token"], dict_channel_id["channel_id"], message)

    notifications_1 = notifications_get_v1(user_2["token"])["notifications"]
    assert len(notifications_1) == 0

def test_one_tag_dm_send(users, channels):

    message_senddm_v1(users[0]["token"], channels[1], "@haydensmith hi")

    notifications = notifications_get_v1(users[1]["token"])["notifications"]

    assert notifications[1]["notification_message"] == "mj added you to haydensmith, mj, nothaydensmith"
    assert notifications[1]["channel_id"] == -1
    assert notifications[1]["dm_id"] == channels[1]

    assert notifications[0]["notification_message"] == "mj tagged you in haydensmith, mj, nothaydensmith: @haydensmith hi"
    assert notifications[0]["channel_id"] == -1
    assert notifications[0]["dm_id"] == channels[1]

def test_several_users_tagged_dm_message(users, channels):

    message = "Welcome to my dm @haydensmith and @nothaydensmith"

    message_senddm_v1(users[0]["token"], channels[1], message)

    cut_message = message[:20]

    notifications_1 = notifications_get_v1(users[1]["token"])["notifications"]
    notifications_2 = notifications_get_v1(users[2]["token"])["notifications"]

    notification_message = f"mj tagged you in haydensmith, mj, nothaydensmith: {cut_message}"

    assert notifications_1[0]["notification_message"] == notification_message
    assert notifications_1[0]["channel_id"] == -1
    assert notifications_1[0]["dm_id"] == channels[1]

    assert notifications_1[1]["notification_message"] == "mj added you to haydensmith, mj, nothaydensmith"
    assert notifications_1[1]["channel_id"] == -1
    assert notifications_1[1]["dm_id"] == channels[1]

    assert notifications_2[0]["notification_message"] == notification_message
    assert notifications_2[0]["channel_id"] == -1
    assert notifications_2[0]["dm_id"] == channels[1]

    assert notifications_2[1]["notification_message"] == "mj added you to haydensmith, mj, nothaydensmith"
    assert notifications_2[1]["channel_id"] == -1
    assert notifications_2[1]["dm_id"] == channels[1]

    clear_v1()

def test_notifications_dm_invite():
    clear_v1()
    notification_message = "mj added you to mj"

    user = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    user_2 = auth_register_v2('anothervalidemail@gmail.com', '123abc!@#', 'Hayden', 'Smith')
    user_3 = auth_register_v2('yetanothervalidemail@gmail.com', '123abc!@#', 'Nothayden', 'Smith')

    dm_id = dm_create_v1(user["token"], [])["dm_id"]

    dm_invite_v1(user["token"], dm_id, user_2["auth_user_id"])
    dm_invite_v1(user["token"], dm_id, user_3["auth_user_id"])


    notifications_1 = notifications_get_v1(user_2["token"])["notifications"]
    notifications_2 = notifications_get_v1(user_3["token"])["notifications"]

    assert notifications_1[0]["notification_message"] == notification_message
    assert notifications_1[0]["channel_id"] == -1
    assert notifications_1[0]["dm_id"] == dm_id

    assert notifications_2[0]["notification_message"] == notification_message
    assert notifications_2[0]["channel_id"] == -1
    assert notifications_2[0]["dm_id"] == dm_id

    clear_v1()