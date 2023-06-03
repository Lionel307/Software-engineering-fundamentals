import pytest

from src.auth import auth_register_v2, auth_logout_v1
from src.message import message_senddm_v1
from src.dm import dm_create_v1, dm_invite_v1, dm_messages_v1
from src.other import clear_v1
from src.error import InputError, AccessError


@pytest.fixture
def users():
    clear_v1()
    user = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    user_2 = auth_register_v2('anothervalidemail@gmail.com', '123abc!@#', 'Hayden', 'Smith')
    user_3 = auth_register_v2('yetanothervalidemail@gmail.com', '123abc!@#', 'Nothayden', 'Smith')
    return [user, user_2, user_3]


@pytest.fixture
def dms(users):
    dict_dm_id = dm_create_v1(users[0]["token"], [])
    dict_dm_id_2 = dm_create_v1(users[1]["token"], [])
    dm_ids = [dict_dm_id['dm_id'], dict_dm_id_2['dm_id']]

    return dm_ids


def test_no_messages(users, dms):
    expected_output = {
        'messages': [],
        'start': 0,
        'end': -1,
    }

    assert dm_messages_v1(users[0]["token"], dms[0], 0) == expected_output


def test_one_message_channel_owner(users, dms):

    message = "comp1531 is fun!!"
    message_id = message_senddm_v1(users[0]["token"], dms[0], message)

    message_list = dm_messages_v1(users[0]["token"], dms[0], 0)

    assert message_list["messages"][0]["u_id"] == users[0]["auth_user_id"]
    assert message_list["messages"][0]["message_id"] == message_id["message_id"]
    assert message_list["messages"][0]["message"] == message

    assert message_list["start"] == 0
    assert message_list["end"] == -1


def test_two_messages(users, dms):

    dm_invite_v1(users[0]["token"], dms[0], users[1]["auth_user_id"])

    message = "comp1531 is fun!!"
    message_2 = "Yes, I love programming in python"
    message_id = message_senddm_v1(users[0]["token"], dms[0], message)
    message_id_2 = message_senddm_v1(users[1]["token"], dms[0], message_2)

    message_list = dm_messages_v1(users[0]["token"], dms[0], 0)

    assert message_list["messages"][1]["u_id"] == users[0]["auth_user_id"]
    assert message_list["messages"][1]["message_id"] == message_id["message_id"]
    assert message_list["messages"][1]["message"] == message

    assert message_list["messages"][0]["u_id"] == users[1]["auth_user_id"]
    assert message_list["messages"][0]["message_id"] == message_id_2["message_id"]
    assert message_list["messages"][0]["message"] == message_2


def test_50_messages(users, dms):

    list_of_messages_sent = []
    list_of_msg_ids = []
    # x goes from 0 to 49
    for x in range(50):
        message = f"test{x}"
        message_id = message_senddm_v1(users[0]["token"], dms[0], message)
        list_of_messages_sent.append(message)
        list_of_msg_ids.append(message_id["message_id"])

    message_list = dm_messages_v1(users[0]["token"], dms[0], 0)

    list_of_msg_ids.reverse()
    list_of_messages_sent.reverse()

    for x in range(50):
        assert list_of_messages_sent[x] == message_list["messages"][x]["message"]
        assert list_of_msg_ids[x] == message_list["messages"][x]["message_id"]
    
    assert message_list["start"] == 0
    assert message_list["end"] == -1


def test_110_messages(users, dms):

    list_of_messages_sent = []
    # x goes from 0 to 109
    for x in range(110):
        message = f"test{x}"
        message_senddm_v1(users[0]["token"], dms[0], message)
        list_of_messages_sent.append(message)

    message_list = dm_messages_v1(users[0]["token"], dms[0], 50)

    list_of_messages_sent.reverse()

    y = 0
    for x in range(50, 100):
        assert list_of_messages_sent[x] == message_list["messages"][y]["message"]
        y = y + 1
    
    assert message_list["start"] == 50
    assert message_list["end"] == 100


def test_invalid_dm(users):
    with pytest.raises(InputError):
        dm_messages_v1(users[0]["token"], 'dm 1', 0)

    with pytest.raises(InputError):
        dm_messages_v1(users[0]["token"], 42, 0)

    with pytest.raises(InputError):
        dm_messages_v1(users[0]["token"], {'dm_id': 42}, 0)


def test_invalid_start(users, dms):
    with pytest.raises(InputError):
        dm_messages_v1(users[0]["token"], dms[0], 14)

    with pytest.raises(InputError):
        dm_messages_v1(users[0]["token"], dms[0], 50)

    with pytest.raises(InputError):
        dm_messages_v1(users[0]["token"], dms[0], 1)


def test_user_not_member(users, dms):
    with pytest.raises(AccessError):
        dm_messages_v1(users[1]["token"], dms[0], 0)


def test_start_too_high(users, dms):
    with pytest.raises(InputError):
        dm_messages_v1(users[0]["token"], dms[0], 10)


def test_invalid_token(users, dms):

    with pytest.raises(AccessError):
        dm_messages_v1("invalid_token", dms[0], 0)

    with pytest.raises(AccessError):
        dm_messages_v1({"user1": "1"}, dms[0], 0)

    auth_logout_v1(users[0]["token"])

    with pytest.raises(AccessError):
        dm_messages_v1(users[0]["token"], dms[0], 0)

    clear_v1()
