import pytest
from time import time

from src.other import standup_start_v1, clear_v1
from src.auth import auth_register_v2
from src.channel import channel_join_v2
from src.channels import channels_create_v2
from src.error import InputError, AccessError


@pytest.fixture
def users():
    '''
    Creates users for use in tests
    '''
    clear_v1()

    user_1 = auth_register_v2("email1@gmail.com", "a123!$%", "user", "1")
    user_2 = auth_register_v2("email2@gmail.com", "a123!$%", "user", "2")
    user_3 = auth_register_v2("email3@gmail.com", "a123!$%", "user", "3")

    list_users = [user_1, user_2, user_3]

    return list_users


@pytest.fixture
def channel_ids(users):
    '''
    Creates the channels for use in tests
    '''
    channel_1 = channels_create_v2(users[0]["token"], "channel 1", True)    
    channel_2 = channels_create_v2(users[1]["token"], "channel 2", True)

    channel_join_v2(users[1]["token"], channel_1['channel_id'])

    list_of_channels = [channel_1['channel_id'], channel_2['channel_id']]

    return list_of_channels


def test_successful_return(users, channel_ids):
    '''
    A test which checks the output of the function to see if it is of the correct type
    '''
    started_standup = standup_start_v1(users[0]["token"], channel_ids[0], 5)

    assert isinstance(started_standup, dict) and isinstance(started_standup["time_finish"], int)


def test_time_finish(users, channel_ids):
    '''
    A test which checks the output of the function to see if the time_finish key is
    in the correct range
    '''
    LENGTH = 5
    current_time = int(time())
    # what time_finish key should be close to (within +2 seconds)
    expected_time_finish = current_time + LENGTH
    expected_time_range = range(expected_time_finish, expected_time_finish + 3)

    started_standup = standup_start_v1(users[0]["token"], channel_ids[0], LENGTH)
    time_stamp = started_standup["time_finish"]

    assert time_stamp in expected_time_range


def test_multiple_channels_running_standups(users, channel_ids):
    '''
    A test which checks the output of the function to see if it is of the correct type
    when there are multiple channels running a standup
    '''
    # length of standup in seconds
    LENGTH = 10

    channel_3 = channels_create_v2(users[2]["token"], "channel 3", True)
    channel_id_3 = channel_3["channel_id"]    

    started_standup_1 = standup_start_v1(users[0]["token"], channel_ids[0], LENGTH)
    started_standup_2 = standup_start_v1(users[1]["token"], channel_ids[1], LENGTH)
    started_standup_3 = standup_start_v1(users[2]["token"], channel_id_3, LENGTH)

    assert isinstance(started_standup_1, dict) and isinstance(started_standup_1["time_finish"], int)
    assert isinstance(started_standup_2, dict) and isinstance(started_standup_2["time_finish"], int)
    assert isinstance(started_standup_3, dict) and isinstance(started_standup_3["time_finish"], int)


def test_invalid_channel(users):
    '''
    A test which checks if an InputError is raised when channel_id is not a 
    valid channel
    '''
    LENGTH = 10
    TOKEN = users[0]["token"]

    with pytest.raises(InputError):
        standup_start_v1(TOKEN, 1, LENGTH)

    with pytest.raises(InputError):
        standup_start_v1(TOKEN, 2, LENGTH)

    with pytest.raises(InputError):
        standup_start_v1(TOKEN, 3, LENGTH)


def test_standup_already_active(users, channel_ids):
    '''
    A test which checks if an InputError is raised when an active standup is
    currently running in the channel with channel_id
    '''
    LENGTH = 10
    TOKEN_1 = users[0]["token"]
    TOKEN_2 = users[1]["token"]

    standup_start_v1(TOKEN_2, channel_ids[0], LENGTH)
    standup_start_v1(TOKEN_2, channel_ids[1], LENGTH)

    with pytest.raises(InputError):
        standup_start_v1(TOKEN_1, channel_ids[0], LENGTH)

    with pytest.raises(InputError):
        standup_start_v1(TOKEN_2, channel_ids[0], LENGTH)

    with pytest.raises(InputError):
        standup_start_v1(TOKEN_2, channel_ids[1], LENGTH)


def test_user_not_member(users, channel_ids):
    '''
    A test which checks if an AccessError is raised when the authorised user
    is not a member of the channel with channel_id
    '''
    LENGTH = 10
    TOKEN_1 = users[0]["token"]
    TOKEN_3 = users[2]["token"]

    with pytest.raises(AccessError):
        standup_start_v1(TOKEN_1, channel_ids[1], LENGTH)

    with pytest.raises(AccessError):
        standup_start_v1(TOKEN_3, channel_ids[0], LENGTH)

    with pytest.raises(AccessError):
        standup_start_v1(TOKEN_3, channel_ids[1], LENGTH)


def test_invalid_token(channel_ids):
    '''
    A test which checks if an AccessError is raised when the token passed in
    is not a valid id
    '''
    LENGTH = 10

    with pytest.raises(AccessError):
        standup_start_v1("invalid token", channel_ids[0], LENGTH)

    with pytest.raises(AccessError):
        standup_start_v1(" ", channel_ids[0], LENGTH)

    with pytest.raises(AccessError):
        standup_start_v1(1, channel_ids[0], LENGTH)

    clear_v1()
