import pytest

from src.channel import channel_invite_v2
from src.channels import channels_list_v2
from src.channels import channels_create_v2
from src.auth import auth_register_v2
from src.error import InputError, AccessError
from src.other import clear_v1


@pytest.fixture
def auth_user():
    '''
    Clears the database and registers user 1 for use in tests
    '''
    clear_v1()
    dict_auth_user_id = auth_register_v2("hi@hi.com", "abcdefgh", "Hayden", "Smith")
    return dict_auth_user_id


@pytest.fixture
def invited_user():
    '''
    Registers the user who will be invited to a channel in tests
    '''
    dict_u_id = auth_register_v2("hola@hi.com", "abcdefgh", "Bob", "Bobson")
    return dict_u_id


@pytest.fixture
def channel_1(auth_user):
    '''
    Creates a channel for use in tests
    '''
    dict_channel_id = channels_create_v2(auth_user['token'], "test", True)
    channel_id = dict_channel_id["channel_id"]

    return channel_id


def test_correct_return(auth_user, channel_1, invited_user):
    '''
    A test which checks if an InputError is raised when the u_id passed in 
    does not refer to a valid user
    '''
    assert channel_invite_v2(auth_user['token'], channel_1, invited_user['auth_user_id']) == {}


def test_invalid_channel(auth_user, invited_user):
    '''
    A test which checks if an InputError is raised when the channel_id passed in 
    does not refer to a valid channel
    '''
    with pytest.raises(InputError):
        channel_invite_v2(auth_user['token'], 6, invited_user['auth_user_id'])
    
    with pytest.raises(InputError):
        channel_invite_v2(auth_user['token'], "invalid", invited_user['auth_user_id'])


def test_invalid_invited_user(auth_user, channel_1):
    '''
    A test which checks if an InputError is raised when the u_id passed in 
    does not refer to a valid user
    '''
    u_id = auth_user['auth_user_id'] + 1
    with pytest.raises(InputError):
        channel_invite_v2(auth_user['token'], channel_1, u_id)


def test_not_member(channel_1, invited_user):
    '''
    A test which checks if an AccessError is raised when the authorised user 
    is not a member of the channel with channel_id
    '''
    u_id_2 = auth_register_v2("hei@hi.com", "abcdefgh", "Boba", "Tea")

    with pytest.raises(AccessError):
        channel_invite_v2(invited_user['auth_user_id'], channel_1, u_id_2['auth_user_id'])


def test_successfully_joined(auth_user, channel_1, invited_user):
    '''
    A test which checks if a user who was invited to a channel 
    successfully joined it
    '''
    channel_invite_v2(auth_user['token'], channel_1, invited_user['auth_user_id'])

    dict_channels = channels_list_v2(invited_user['token'])
    list_channels = dict_channels["channels"]

    is_member = False
    for channel in list_channels:
        if channel["channel_id"] == channel_1:
            is_member = True

    assert is_member == True


def test_private_channel(auth_user, invited_user):
    '''
    A test which checks if a user who was invited to a private channel 
    successfully joined it
    '''
    dict_channel_id = channels_create_v2(auth_user['token'], "test", False)
    channel_id = dict_channel_id["channel_id"]

    channel_invite_v2(auth_user['token'], channel_id, invited_user['auth_user_id'])

    dict_channels = channels_list_v2(invited_user['token'])
    list_channels = dict_channels["channels"]

    is_member = False
    for channel in list_channels:
        if channel["channel_id"] == channel_id:
            is_member = True

    assert is_member == True


def test_invalid_token(channel_1, invited_user):
    '''
    A test which checks if an AccessError is raised when the token passed in
    is not a valid id
    '''
    with pytest.raises(AccessError):
        channel_invite_v2("invalid_id", channel_1, invited_user['auth_user_id'])

    with pytest.raises(AccessError):
        channel_invite_v2({}, channel_1, invited_user['auth_user_id'])

    with pytest.raises(AccessError):
        channel_invite_v2([1, 2, 3], channel_1, invited_user['auth_user_id'])

    with pytest.raises(AccessError):
        channel_invite_v2({'hello': 1}, channel_1, invited_user['auth_user_id'])

    clear_v1()
