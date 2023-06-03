import pytest

from src.channel import channel_messages_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError, AccessError


@pytest.fixture
def user_1():
    clear_v1()
    dict_auth_user_id_1 = auth_register_v1('validemail@gmail.com', '123abc!@#', 'M', 'J')
    auth_user_id_1 = dict_auth_user_id_1['auth_user_id'] 

    return auth_user_id_1


@pytest.fixture
def user_2():
    dict_auth_user_id_2 = auth_register_v1('anotherEmail@gmail.com', '5823afc!@#', 'A', 'I')
    auth_user_id_2 = dict_auth_user_id_2['auth_user_id'] 

    return auth_user_id_2


@pytest.fixture
def channel_1(user_1):
    dict_channel_id = channels_create_v1(user_1, "user 1's channel", True)
    channel_id = dict_channel_id['channel_id']

    return channel_id


def test_no_messages(user_1, channel_1):
    expected_output = {
        'messages': [],
        'start': 0,
        'end': -1,
    }

    assert channel_messages_v1(user_1, channel_1, 0) == expected_output


def test_invalid_channel(user_1):
    with pytest.raises(InputError):
        assert channel_messages_v1(user_1, 'channel 1', 0)

    with pytest.raises(InputError):
        assert channel_messages_v1(user_1, 1, 0)

    with pytest.raises(InputError):
        assert channel_messages_v1(user_1, {'channel_id': 1}, 0)


def test_invalid_start(user_1, channel_1):
    with pytest.raises(InputError):
        assert channel_messages_v1(user_1, channel_1, 25)

    with pytest.raises(InputError):
        assert channel_messages_v1(user_1, channel_1, 50)

    with pytest.raises(InputError):
        assert channel_messages_v1(user_1, channel_1, 100)


def test_user_not_member(user_2, channel_1):
    with pytest.raises(AccessError):
        assert channel_messages_v1(user_2, channel_1, 0)


def test_invalid_user_1(user_1, channel_1):
    with pytest.raises(AccessError):
        assert channel_messages_v1(user_1 + 1, channel_1, 0)
    
    with pytest.raises(AccessError):
        assert channel_messages_v1(user_1 + 2, channel_1, 0)

    with pytest.raises(AccessError):
        assert channel_messages_v1(user_1 + 3, channel_1, 0)


def test_invalid_user_2(channel_1):
    with pytest.raises(AccessError):
        assert channel_messages_v1({'user_1': 1}, channel_1, 0)
    
    with pytest.raises(AccessError):
        assert channel_messages_v1('user_1', channel_1, 0)

    with pytest.raises(AccessError):
        assert channel_messages_v1([1, 2, 3], channel_1, 0)
    
    with pytest.raises(AccessError):
        assert channel_messages_v1((1, 2, 3), channel_1, 0)
