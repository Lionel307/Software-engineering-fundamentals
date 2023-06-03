import pytest

from src.other import standup_start_v1, standup_active_v1, clear_v1
from src.auth import auth_register_v2
from src.channel import channel_join_v2
from src.channels import channels_create_v2
from src.error import InputError, AccessError


@pytest.fixture
def token_1():
    '''
    Creates a user for use in tests
    '''
    clear_v1()

    user = auth_register_v2("email1@gmail.com", "a123!$%", "user", "1")

    return user["token"]


@pytest.fixture
def channel_id_1(token_1):
    '''
    Creates a channel for use in tests
    '''
    channel_1 = channels_create_v2(token_1, "channel 1", True)    

    return channel_1["channel_id"]


@pytest.fixture
def start_standup(token_1, channel_id_1):
    '''
    Starts a standup for use in tests
    '''
    started_standup = standup_start_v1(token_1, channel_id_1, 5)

    return started_standup


def test_success_standup_active(token_1, channel_id_1, start_standup):
    '''
    A test which checks if the return values of the function are correct when a standup
    is active in channel with channel_id
    '''
    standup_status = standup_active_v1(token_1, channel_id_1)

    assert standup_status["is_active"] == True


def test_success_time_finish(token_1, channel_id_1, start_standup):
    '''
    A test which checks if the time_finish key in the output is correct
    '''
    standup_status = standup_active_v1(token_1, channel_id_1)

    assert isinstance(standup_status["time_finish"], int) == True
    assert standup_status["time_finish"] == start_standup["time_finish"]


def test_success_standup_not_active(token_1, channel_id_1):
    '''
    A test which checks if the return values of the function are correct when a standup
    is not active in channel with channel_id
    '''
    standup_status = standup_active_v1(token_1, channel_id_1)

    assert standup_status["is_active"] == False and standup_status["time_finish"] is None


def test_invalid_channel(token_1):
    '''
    A test which checks if an InputError is raised when channel_id is not a 
    valid channel
    '''
    with pytest.raises(InputError):
        standup_active_v1(token_1, 1)

    with pytest.raises(InputError):
        standup_active_v1(token_1, 2)

    with pytest.raises(InputError):
        standup_active_v1(token_1, 3)


def test_invalid_token(channel_id_1):
    '''
    A test which checks if an AccessError is raised when the token passed in
    is not a valid id
    '''
    with pytest.raises(AccessError):
        standup_active_v1("invalid token", channel_id_1)

    with pytest.raises(AccessError):
        standup_active_v1(" ", channel_id_1)

    with pytest.raises(AccessError):
        standup_active_v1(1, channel_id_1)

    clear_v1()
