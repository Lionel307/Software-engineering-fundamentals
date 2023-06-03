import pytest

from src.error import InputError, AccessError
from src.other import clear_v1
from src.channel import channel_join_v1, channel_details_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1


#  Registers users for use in tests
@pytest.fixture
def auth_users():
    clear_v1()
    auth_user_1 = auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    auth_user_1 = auth_user_1['auth_user_id']
    auth_user_2 = auth_register_v1('random@gmail.com', '!@#123abc', 'Random', 'Name')
    auth_user_2 = auth_user_2['auth_user_id']
    auth_user_3 = auth_register_v1('dj@gmail.com', '!@#123abc', 'Doris', 'Johnson')
    auth_user_3 = auth_user_3['auth_user_id']
    list_of_user_id = [auth_user_1, auth_user_2, auth_user_3]
    return list_of_user_id


#  Creates the channels for use in tests
@pytest.fixture
def channel_id_dict(auth_users):

    name = ["hello", "hi", "hola", "hallo"]

    channel_id_1 = channels_create_v1(auth_users[0], name[0], True)
    channel_id_1 = channel_id_1['channel_id']
    channel_id_2 = channels_create_v1(auth_users[1], name[1], True)
    channel_id_2 = channel_id_2['channel_id']
    channel_id_3 = channels_create_v1(auth_users[2], name[2], True)
    channel_id_3 = channel_id_3['channel_id']
    private_channel_id = channels_create_v1(auth_users[2], name[3], False)
    private_channel_id = private_channel_id['channel_id']

    dict_of_ids = {
        'channel_id_1': channel_id_1,
        'channel_id_2': channel_id_2,
        'channel_id_3': channel_id_3,
        'private_channel_id': private_channel_id,

    }
    return dict_of_ids


# Tests that the return value of the function is correct
def test_auth_user_join_correct_return(auth_users, channel_id_dict):
    assert channel_join_v1(auth_users[0], channel_id_dict['channel_id_1']) == {}


#  Tests that the user joined the channel
def test_channel_joined(auth_users, channel_id_dict):
    channel_join_v1(auth_users[0], channel_id_dict['channel_id_2'])
    channel_join_v1(auth_users[0], channel_id_dict['channel_id_3'])
    channel_join_v1(auth_users[1], channel_id_dict['channel_id_1'])
    channel_join_v1(auth_users[1], channel_id_dict['channel_id_3'])
    channel_join_v1(auth_users[2], channel_id_dict['channel_id_1'])
    channel_join_v1(auth_users[2], channel_id_dict['channel_id_2'])

    flag = False
    channel_1_details = channel_details_v1(auth_users[0], channel_id_dict['channel_id_1'])
    channel_1_details = channel_1_details['all_members']
    for member in channel_1_details:
        if auth_users[1] == member['u_id']:
            flag = True
    assert flag == True

    flag = False
    for member in channel_1_details:
        if auth_users[2] == member['u_id']:
            flag = True
    assert flag == True

    flag = False
    channel_2_details = channel_details_v1(auth_users[1], channel_id_dict['channel_id_2'])
    channel_2_details = channel_2_details['all_members']
    for member in channel_2_details:
        if auth_users[0] == member['u_id']:
            flag = True
    assert flag == True

    flag = False
    for member in channel_2_details:
        if auth_users[2] == member['u_id']:
            flag = True
    assert flag == True

    flag = False
    channel_3_details = channel_details_v1(auth_users[2], channel_id_dict['channel_id_3'])
    channel_3_details = channel_3_details['all_members']
    for member in channel_3_details:
        if auth_users[0] == member['u_id']:
            flag = True
    assert flag == True

    flag = False
    for member in channel_3_details:
        if auth_users[1] == member['u_id']:
            flag = True
    assert flag == True


# channel id doesnt exist
def test_not_valid_channel(auth_users):
    with pytest.raises(InputError):
        channel_join_v1(auth_users[0], 123456)


# Tests that AccessError is raised when trying to join a private channel
def test_private_channel(auth_users, channel_id_dict):

    with pytest.raises(AccessError):
        channel_join_v1(auth_users[1], channel_id_dict['private_channel_id'])


# Checks that global owner can join private channels
def test_private_channel_global_owner(auth_users, channel_id_dict):

    channel_join_v1(auth_users[0], channel_id_dict['private_channel_id'])

    flag = False
    c_d4 = channel_details_v1(auth_users[2], channel_id_dict['private_channel_id'])
    c_d4 = c_d4['all_members']
    for member in c_d4:
        if auth_users[0] == member['u_id']:
            flag = True
    assert flag == True


# Tests that AccessError is raised when the auth_user_id is invalid or of invalid type
def test_invalid_auth_id(auth_users, channel_id_dict):

    with pytest.raises(AccessError):
        channel_join_v1(42, channel_id_dict['channel_id_1'])

    with pytest.raises(AccessError):
        channel_join_v1('h', channel_id_dict['channel_id_1'])

    with pytest.raises(AccessError):
        channel_join_v1("hello", channel_id_dict['channel_id_1'])

    with pytest.raises(AccessError):
        channel_join_v1([], channel_id_dict['channel_id_1'])

    with pytest.raises(AccessError):
        channel_join_v1({}, channel_id_dict['channel_id_1'])
