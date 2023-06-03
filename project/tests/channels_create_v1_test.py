import pytest

from src.channels import channels_create_v1, channels_listall_v1
from src.auth import auth_login_v1, auth_register_v1
from src.error import InputError, AccessError
from src.other import clear_v1


@pytest.fixture
def auth_id():
    clear_v1()
    a = auth_register_v1("hi@hi.com", "abcdefgh", "Hayden", "Smith")
    auth_id = a["auth_user_id"]
    return auth_id


def test_correct_return_type(auth_id):
    
    c = channels_create_v1(auth_id, "test", True)
    assert isinstance(c, dict) == True


def test_long_name(auth_id):

    with pytest.raises(InputError):
        channels_create_v1(auth_id, "abcdefghijklmnopqrstuvw", True)
    with pytest.raises(InputError):
        channels_create_v1(auth_id, "123456789112345678911", True)


def test_channel_created(auth_id):

    name = "test"
    c = channels_create_v1(auth_id, name, True)
    channel_id = c["channel_id"]

    c = channels_listall_v1(auth_id)
    c_list = c["channels"]

    flag = 0

    for a in c_list:
        if a["channel_id"] == channel_id and a["name"] == name:
            flag = 1
    assert flag == 1


def test_20_char_name(auth_id):

    name = "Overenthusiastically"
    c = channels_create_v1(auth_id, name, True)
    channel_id = c["channel_id"]

    c = channels_listall_v1(auth_id)
    c_list = c["channels"]

    flag = 0

    for a in c_list:
        if a["channel_id"] == channel_id and a["name"] == name:
            flag = 1
    assert flag == 1


def test_several_channels(auth_id):

    name = ["channel1", "channel2", "channel3", "channel4"]
    c = channels_create_v1(auth_id, name[0], True)
    channel_id1 = c["channel_id"]
    c = channels_create_v1(auth_id, name[1], True)
    channel_id2 = c["channel_id"]
    c = channels_create_v1(auth_id, name[2], True)
    channel_id3 = c["channel_id"]
    c = channels_create_v1(auth_id, name[3], True)
    channel_id4 = c["channel_id"]

    c = channels_listall_v1(auth_id)
    c_list = c["channels"]

    flag = [0, 0, 0, 0]

    for a in c_list:
        if a["channel_id"] == channel_id1 and a["name"] == name[0]:
            flag[0] = 1
    for a in c_list:
        if a["channel_id"] == channel_id2 and a["name"] == name[1]:
            flag[1] = 1
    for a in c_list:
        if a["channel_id"] == channel_id3 and a["name"] == name[2]:
            flag[2] = 1
    for a in c_list:
        if a["channel_id"] == channel_id4 and a["name"] == name[3]:
            flag[3] = 1
    
    for a in flag:
        assert flag[a] == 1


def test_invalid_auth_id(auth_id):

    auth_id = auth_id + 1

    with pytest.raises(AccessError):
        channels_create_v1(auth_id, "abcdefg", True)

    auth_id = 'hi'
    with pytest.raises(AccessError):
        channels_create_v1(auth_id, "1234567", True)

    auth_id = {}
    with pytest.raises(AccessError):
        channels_create_v1(auth_id, "1234567", True)

    auth_id = {'hello': 1}
    with pytest.raises(AccessError):
        channels_create_v1(auth_id, "1234567", True)
