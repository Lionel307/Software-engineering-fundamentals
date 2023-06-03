import pytest
from src.channel import channel_messages_v2, channel_join_v2
from src.channels import channels_create_v2
from src.auth import auth_register_v2, auth_logout_v1
from src.message import message_send_v2
from src.other import clear_v1
from src.error import InputError, AccessError


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

def test_no_messages(users, channels):
    expected_output = {
        'messages': [],
        'start': 0,
        'end': -1,
    }

    assert channel_messages_v2(users[0]["token"], channels[0], 0) == expected_output

def test_one_message_channel_owner(users, channels):

    message = "comp1531 is fun!!"
    message_id = message_send_v2(users[0]["token"], channels[0], message)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)

    assert message_list["messages"][0]["u_id"] == users[0]["auth_user_id"]
    assert message_list["messages"][0]["message_id"] == message_id["message_id"]
    assert message_list["messages"][0]["message"] == message

    assert message_list["start"] == 0
    assert message_list["end"] == -1

def test_two_messages(users, channels):

    channel_join_v2(users[1]["token"], channels[0])

    message = "comp1531 is fun!!"
    message_2 = "Yes, I love programming in python"
    message_id = message_send_v2(users[0]["token"], channels[0], message)
    message_id_2 = message_send_v2(users[1]["token"], channels[0], message_2)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)

    assert message_list["messages"][1]["u_id"] == users[0]["auth_user_id"]
    assert message_list["messages"][1]["message_id"] == message_id["message_id"]
    assert message_list["messages"][1]["message"] == message

    assert message_list["messages"][0]["u_id"] == users[1]["auth_user_id"]
    assert message_list["messages"][0]["message_id"] == message_id_2["message_id"]
    assert message_list["messages"][0]["message"] == message_2


def test_50_messages(users, channels):

    list_of_messages_sent = []
    list_of_msg_ids = []
    # x goes from 0 to 49
    for x in range(50):
        message = f"test{x}"
        message_id = message_send_v2(users[0]["token"], channels[0], message)
        list_of_messages_sent.append(message)
        list_of_msg_ids.append(message_id["message_id"])

    message_list = channel_messages_v2(users[0]["token"], channels[0], 0)

    list_of_msg_ids.reverse()
    list_of_messages_sent.reverse()

    for x in range(50):
        assert list_of_messages_sent[x] == message_list["messages"][x]["message"]
        assert list_of_msg_ids[x] == message_list["messages"][x]["message_id"]
    
    assert message_list["start"] == 0
    assert message_list["end"] == -1

def test_110_messages(users, channels):

    list_of_messages_sent = []
    list_of_message_ids = []
    # x goes from 0 to 109
    for x in range(110):
        message = f"test{x}"
        message_id = message_send_v2(users[0]["token"], channels[0], message)["message_id"]
        list_of_messages_sent.append(message)
        list_of_message_ids.append(message_id)

    message_list = channel_messages_v2(users[0]["token"], channels[0], 50)

    list_of_messages_sent.reverse()
    list_of_message_ids.reverse()

    y = 0
    for x in range(50, 100):
        assert list_of_messages_sent[x] == message_list["messages"][y]["message"]
        assert list_of_message_ids[x] == message_list["messages"][y]["message_id"]
        y = y + 1
    
    assert message_list["start"] == 50
    assert message_list["end"] == 100

def test_invalid_channel(users):
    with pytest.raises(InputError):
        channel_messages_v2(users[0]["token"], 'channel 1', 0)

    with pytest.raises(InputError):
        channel_messages_v2(users[0]["token"], 42, 0)

    with pytest.raises(InputError):
        channel_messages_v2(users[0]["token"], {'channel_id': 42}, 0)

def test_user_not_member(users, channels):
    with pytest.raises(AccessError):
        channel_messages_v2(users[1]["token"], channels[0], 0)



def test_invalid_token(users, channels):

    with pytest.raises(AccessError):
        channel_messages_v2("invalid_token", channels[0], 0)

    with pytest.raises(AccessError):
        channel_messages_v2({"user1": "1"}, channels[0], 0)

    auth_logout_v1(users[0]["token"])

    with pytest.raises(AccessError):
        channel_messages_v2(users[0]["token"], channels[0], 0)

    clear_v1()