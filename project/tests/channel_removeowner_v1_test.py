import pytest

from src.channel import channel_removeowner_v1, channel_addowner_v1
from src.channel import channel_details_v2, channel_join_v2
from src.channels import channels_create_v2
from src.auth import auth_register_v2
from src.other import clear_v1
from src.error import InputError, AccessError


@pytest.fixture
def auth_users():
    '''
    Registers users for use in tests
    '''
    clear_v1()

    user_1 = auth_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    user_2 = auth_register_v2('random@gmail.com', '!@#123abc', 'Random', 'Name')
    user_3 = auth_register_v2('dj@gmail.com', '!@#123abc', 'Doris', 'Johnson')
    list_of_users = [user_1, user_2, user_3]
    
    return list_of_users


@pytest.fixture
def channel_ids(auth_users):
    '''
    Creates the channels for use in tests
    '''
    name = ["hello", "hi", "hola", "hallo"]

    dict_channel_id_1 = channels_create_v2(auth_users[0]["token"], name[0], True)
    channel_id_1 = dict_channel_id_1['channel_id']
    dict_channel_id_2 = channels_create_v2(auth_users[1]["token"], name[1], True)
    channel_id_2 = dict_channel_id_2['channel_id']
    dict_channel_id_3 = channels_create_v2(auth_users[2]["token"], name[2], True)
    channel_id_3 = dict_channel_id_3['channel_id']

    list_of_channels = [channel_id_1, channel_id_2, channel_id_3]

    return list_of_channels


def test_correct_return(auth_users, channel_ids):
    '''
    A test which checks if the return value of the function is correct
    '''
    channel_join_v2(auth_users[1]["token"], channel_ids[0])
    channel_addowner_v1(auth_users[0]["token"], channel_ids[0], auth_users[1]["auth_user_id"])

    assert channel_removeowner_v1(auth_users[0]["token"], channel_ids[0], auth_users[1]["auth_user_id"]) == {}


def test_removed_owner(auth_users, channel_ids):
    '''
    A test which checks if the user was successfully removed as an owner of the channel
    '''
    channel_join_v2(auth_users[0]["token"], channel_ids[2])
    channel_join_v2(auth_users[1]["token"], channel_ids[2])
    channel_addowner_v1(auth_users[0]["token"], channel_ids[2], auth_users[1]["auth_user_id"])
    channel_removeowner_v1(auth_users[1]["token"], channel_ids[2], auth_users[2]["auth_user_id"])

    c_details = channel_details_v2(auth_users[2]["token"], channel_ids[2])
    list_owners = c_details['owner_members']
    list_members = c_details['all_members']

    is_owner = False
    for owner in list_owners:
        if owner['u_id'] == auth_users[2]["auth_user_id"]:
            is_owner = True
    
    is_member = False
    for member in list_members:
        if member['u_id'] == auth_users[2]["auth_user_id"]:
            is_member = True

    assert is_owner == False
    assert is_member == True


def test_global_owner_removed_owner(auth_users, channel_ids):
    '''
    A test which checks if the user was successfully removed as an owner of the channel
    by an owner of Dreams
    '''
    channel_join_v2(auth_users[0]["token"], channel_ids[2])
    channel_join_v2(auth_users[1]["token"], channel_ids[2])
    channel_addowner_v1(auth_users[0]["token"], channel_ids[2], auth_users[1]["auth_user_id"])
    channel_removeowner_v1(auth_users[0]["token"], channel_ids[2], auth_users[2]["auth_user_id"])

    c_details = channel_details_v2(auth_users[2]["token"], channel_ids[2])
    list_owners = c_details['owner_members']
    list_members = c_details['all_members']

    is_owner = False
    for owner in list_owners:
        if owner['u_id'] == auth_users[2]["auth_user_id"]:
            is_owner = True
    
    is_member = False
    for member in list_members:
        if member['u_id'] == auth_users[2]["auth_user_id"]:
            is_member = True

    assert is_owner == False
    assert is_member == True


def test_invalid_channel(auth_users):
    '''
    A test which checks if an InputError is raised when the channel_id passed 
    in is not a valid channel
    '''
    with pytest.raises(InputError):
        channel_removeowner_v1(auth_users[0]["token"], "", auth_users[1]["auth_user_id"])

    with pytest.raises(InputError):
        channel_removeowner_v1(auth_users[0]["token"], 1, auth_users[1]["auth_user_id"])

    with pytest.raises(InputError):
        channel_removeowner_v1(auth_users[0]["token"], {}, auth_users[1]["auth_user_id"])

    with pytest.raises(InputError):
        channel_removeowner_v1(auth_users[0]["token"], "invalid_channel", auth_users[1])


def test_user_not_owner(auth_users, channel_ids):
    '''
    A test which checks if an InputError is raised when the user with user id u_id
    is not an owner of the channel
    '''
    channel_join_v2(auth_users[0]["token"], channel_ids[2])
    channel_join_v2(auth_users[1]["token"], channel_ids[2])
    
    with pytest.raises(InputError):
        channel_removeowner_v1(auth_users[2]["token"], channel_ids[2], auth_users[0]["auth_user_id"])

    with pytest.raises(InputError):
        channel_removeowner_v1(auth_users[2]["token"], channel_ids[2], auth_users[1]["auth_user_id"])


def test_only_owner(auth_users, channel_ids):
    '''
    A test which checks if an InputError is raised when the user is the only
    owner of the channel
    '''
    with pytest.raises(InputError):
        channel_removeowner_v1(auth_users[0]["token"], channel_ids[0], auth_users[0]["auth_user_id"])

    with pytest.raises(InputError):
        channel_removeowner_v1(auth_users[1]["token"], channel_ids[1], auth_users[1]["auth_user_id"])

    with pytest.raises(InputError):
        channel_removeowner_v1(auth_users[2]["token"], channel_ids[2], auth_users[2]["auth_user_id"])


def test_auth_user_not_owner(auth_users, channel_ids):
    '''
    A test which checks if an AccessError is raised when the authorised user
    is not an owner of Dreams, or an owner of the channel
    '''
    channel_join_v2(auth_users[1]["token"], channel_ids[0])
    channel_join_v2(auth_users[2]["token"], channel_ids[1])
    channel_join_v2(auth_users[1]["token"], channel_ids[2])

    with pytest.raises(AccessError):
        channel_removeowner_v1(auth_users[1]["token"], channel_ids[0], auth_users[0]["auth_user_id"])
    
    with pytest.raises(AccessError):
        channel_removeowner_v1(auth_users[2]["token"], channel_ids[1], auth_users[1]["auth_user_id"])

    with pytest.raises(AccessError):
        channel_removeowner_v1(auth_users[1]["token"], channel_ids[2], auth_users[2]["auth_user_id"])


def test_invalid_token(auth_users, channel_ids):
    '''
    A test which checks if an AccessError is raised when the token passed in 
    is not valid
    '''
    channel_join_v2(auth_users[1]["token"], channel_ids[0])
    channel_addowner_v1(auth_users[0]["token"], channel_ids[0], auth_users[1]["auth_user_id"])

    with pytest.raises(AccessError):
        channel_removeowner_v1('', channel_ids[0], auth_users[1]["auth_user_id"])

    with pytest.raises(AccessError):
        channel_removeowner_v1('invalid token', channel_ids[0], auth_users[1]["auth_user_id"])

    with pytest.raises(AccessError):
        channel_removeowner_v1([1, 2, 3], channel_ids[0], auth_users[1]["auth_user_id"])

    with pytest.raises(AccessError):
        channel_removeowner_v1((1, 2, 3), channel_ids[0], auth_users[1]["auth_user_id"])

    with pytest.raises(AccessError):
        channel_removeowner_v1({}, channel_ids[0], auth_users[1]["auth_user_id"])

    # To clear the persistent data file once all the tests have been executed
    clear_v1()
