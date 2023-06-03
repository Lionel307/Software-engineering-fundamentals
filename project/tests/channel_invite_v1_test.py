import pytest

from src.channel import channel_invite_v1
from src.channels import channels_list_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.other import clear_v1


@pytest.fixture
def auth_user():
    clear_v1()

    dict_auth_user_id = auth_register_v1("hi@hi.com", "abcdefgh", "Hayden", "Smith")
    auth_user_id = dict_auth_user_id["auth_user_id"]

    return auth_user_id


@pytest.fixture
def invited_user():
    dict_u_id = auth_register_v1("hola@hi.com", "abcdefgh", "Bob", "Bobson")
    u_id = dict_u_id["auth_user_id"]

    return u_id


@pytest.fixture
def channel_1(auth_user):
    dict_channel_id = channels_create_v1(auth_user, "test", True)
    channel_id = dict_channel_id["channel_id"]

    return channel_id


def test_correct_return(auth_user, channel_1, invited_user):
    assert channel_invite_v1(auth_user, channel_1, invited_user) == {}


def test_invalid_channel(auth_user, invited_user):
    with pytest.raises(InputError):
        channel_invite_v1(auth_user, 6, invited_user)
    
    with pytest.raises(InputError):
        channel_invite_v1(auth_user, "invalid", invited_user)


def test_invalid_invited_user(auth_user, channel_1):
    u_id = auth_user + 1
    with pytest.raises(InputError):
        channel_invite_v1(auth_user, channel_1, u_id)


def test_not_member(channel_1, invited_user):
    dict_u_id_2 = auth_register_v1("hei@hi.com", "abcdefgh", "Boba", "Tea")
    u_id_2 = dict_u_id_2["auth_user_id"]
    
    with pytest.raises(AccessError):
        channel_invite_v1(invited_user, channel_1, u_id_2)


def test_successfully_joined(auth_user, channel_1, invited_user):
    channel_invite_v1(auth_user, channel_1, invited_user)

    dict_channels = channels_list_v1(invited_user)
    list_channels = dict_channels["channels"]

    is_member = False
    for channel in list_channels:
        if channel["channel_id"] == channel_1:
            is_member = True

    assert is_member == True


def test_private_channel(auth_user, invited_user):
    dict_channel_id = channels_create_v1(auth_user, "test", False)
    channel_id = dict_channel_id["channel_id"]

    channel_invite_v1(auth_user, channel_id, invited_user)

    dict_channels = channels_list_v1(invited_user)
    list_channels = dict_channels["channels"]

    is_member = False
    for channel in list_channels:
        if channel["channel_id"] == channel_id:
            is_member = True

    assert is_member == True


def test_invalid_auth_user_id(channel_1, invited_user):
    with pytest.raises(AccessError):
        channel_invite_v1("invalid_id", channel_1, invited_user)

    with pytest.raises(AccessError):
        channel_invite_v1({}, channel_1, invited_user)

    with pytest.raises(AccessError):
        channel_invite_v1([1, 2, 3], channel_1, invited_user)

    with pytest.raises(AccessError):
        channel_invite_v1({'hello': 1}, channel_1, invited_user)
