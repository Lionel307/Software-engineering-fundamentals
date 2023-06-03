import pytest

from src.channel import channel_leave_v1, channel_join_v2, channel_details_v2
from src.channel import channel_addowner_v1, channel_messages_v2
from src.channels import channels_create_v2
from src.auth import auth_register_v2
from src.message import message_send_v2
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
    list_of_users = [user_1, user_2]
    
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

    list_of_channels = [channel_id_1, channel_id_2]

    return list_of_channels


def test_correct_return(auth_users, channel_ids):
    '''
    Checks if the return value of the function is correct
    '''
    channel_join_v2(auth_users[1]["token"], channel_ids[0])

    assert channel_leave_v1(auth_users[1]["token"], channel_ids[0]) == {}


def test_channel_left(auth_users, channel_ids):
    '''
    Checks if the user has left the channel successfully
    '''
    channel_join_v2(auth_users[1]["token"], channel_ids[0])
    channel_leave_v1(auth_users[1]["token"], channel_ids[0])

    c_details = channel_details_v2(auth_users[0]["token"], channel_ids[0])
    list_members = c_details['all_members']

    member_removed = True
    for member in list_members:
        if member['u_id'] == auth_users[1]["auth_user_id"]:
            member_removed = False

    assert member_removed == True


def test_channel_owner_left(auth_users, channel_ids):
    '''
    Checks if the user, who is an owner of the channel has left 
    the channel successfully
    '''
    channel_join_v2(auth_users[1]["token"], channel_ids[0])
    channel_addowner_v1(auth_users[0]["token"], channel_ids[0], auth_users[1]["auth_user_id"])
    channel_leave_v1(auth_users[0]["token"], channel_ids[0])

    c_details = channel_details_v2(auth_users[1]["token"], channel_ids[0])
    list_owners = c_details['owner_members']
    list_members = c_details['all_members']

    owner_removed = True
    for owner in list_owners:
        if owner['u_id'] == auth_users[0]["auth_user_id"]:
            owner_removed = False

    member_removed = True
    for member in list_members:
        if member['u_id'] == auth_users[0]["auth_user_id"]:
            member_removed = False

    assert owner_removed == True
    assert member_removed == True


def test_sent_messages(auth_users, channel_ids):
    '''
    Checks if the messages sent by a user who left remain the same
    '''
    channel_join_v2(auth_users[1]["token"], channel_ids[0])

    MESSAGE = "Hello"
    message_id = message_send_v2(auth_users[1]["token"], channel_ids[0], MESSAGE)
    message_id = message_id['message_id']
    
    channel_leave_v1(auth_users[1]["token"], channel_ids[0])

    c_messages = channel_messages_v2(auth_users[0]["token"], channel_ids[0], 0)
    list_messages = c_messages['messages']

    assert list_messages[0]['message_id'] == message_id
    assert list_messages[0]['message'] == MESSAGE


def test_invalid_channel(auth_users):
    '''
    Tests that InputError is raised when the channel_id passed 
    in is not a valid channel
    '''
    with pytest.raises(InputError):
        channel_leave_v1(auth_users[0]["token"], "")
    
    with pytest.raises(InputError):
        channel_leave_v1(auth_users[0]["token"], 1)

    with pytest.raises(InputError):
        channel_leave_v1(auth_users[0]["token"], {})

    with pytest.raises(InputError):
        channel_leave_v1(auth_users[0]["token"], "invalid_channel")


def test_not_member(auth_users, channel_ids):
    '''
    Tests that AccessError is raised when the authorised user is not 
    a member of the channel with channel_id
    '''
    with pytest.raises(AccessError):
        channel_leave_v1(auth_users[0]["token"], channel_ids[1])

    with pytest.raises(AccessError):
        channel_leave_v1(auth_users[1]["token"], channel_ids[0])


def test_invalid_token(channel_ids):
    '''
    A test which checks if an AccessError is raised when the token passed in 
    is not valid
    '''
    with pytest.raises(AccessError):
        channel_leave_v1('', channel_ids[0])

    with pytest.raises(AccessError):
        channel_leave_v1('invalid token', channel_ids[0])

    with pytest.raises(AccessError):
        channel_leave_v1([1, 2, 3], channel_ids[0])

    with pytest.raises(AccessError):
        channel_leave_v1((1, 2, 3), channel_ids[0])

    with pytest.raises(AccessError):
        channel_leave_v1({}, channel_ids[0])

    # To clear the persistent data file once all the tests have been executed
    clear_v1()
