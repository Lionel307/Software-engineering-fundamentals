import pytest

from src.channel import channel_details_v1, channel_invite_v1
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
    dict_auth_user_id_2 = auth_register_v1('another.email@gmail.com', '5823afc!@#', 'A', 'I')    
    auth_user_id_2 = dict_auth_user_id_2['auth_user_id'] 

    return auth_user_id_2


@pytest.fixture
def channel_1(user_1):
    dict_channel_id = channels_create_v1(user_1, "user 1's channel", True)
    channel_id = dict_channel_id['channel_id']

    return channel_id


def test_one_member(user_1, channel_1):
    expected_output = {
        'name': "user 1's channel",
        'is_public': True,
        'owner_members': [
            {
                'u_id': user_1,
                'email': 'validemail@gmail.com',
                'name_first': 'M',
                'name_last': 'J',
                'handle_str': 'mj'
            },
        ],
        'all_members': [
            {
                'u_id': user_1,
                'email': 'validemail@gmail.com',
                'name_first': 'M',
                'name_last': 'J',
                'handle_str': 'mj'
            },
        ],
    }

    assert channel_details_v1(user_1, channel_1) == expected_output


def test_multiple_members(user_1, user_2, channel_1):
    channel_invite_v1(user_1, channel_1, user_2)

    expected_output = {
        'name': "user 1's channel",
        'is_public': True,
        'owner_members': [
            {
                'u_id': user_1,
                'email': 'validemail@gmail.com',
                'name_first': 'M',
                'name_last': 'J',
                'handle_str': 'mj'
            },
        ],
        'all_members': [
            {
                'u_id': user_1,
                'email': 'validemail@gmail.com',
                'name_first': 'M',
                'name_last': 'J',
                'handle_str': 'mj'
            },
            {
                'u_id': user_2,
                'email': 'another.email@gmail.com',
                'name_first': 'A',
                'name_last': 'I',
                'handle_str': 'ai'
            },
        ],
    }
    
    assert channel_details_v1(user_1, channel_1) == expected_output
    assert channel_details_v1(user_2, channel_1) == expected_output


def test_invalid_channel(user_1):
    with pytest.raises(InputError):
        assert channel_details_v1(user_1, 'channel 1')

    with pytest.raises(InputError):
        assert channel_details_v1(user_1, 1)

    with pytest.raises(InputError):
        assert channel_details_v1(user_1, {'channel_id': 1})


def test_user_not_member(user_2, channel_1):
    with pytest.raises(AccessError):
        assert channel_details_v1(user_2, channel_1)


def test_invalid_user_1(user_1, channel_1):
    with pytest.raises(AccessError):
        assert channel_details_v1(user_1 + 1, channel_1)
    
    with pytest.raises(AccessError):
        assert channel_details_v1(user_1 + 2, channel_1)

    with pytest.raises(AccessError):
        assert channel_details_v1(user_1 + 3, channel_1)


def test_invalid_user_2(channel_1):
    with pytest.raises(AccessError):
        assert channel_details_v1({'user_1': 1}, channel_1)
    
    with pytest.raises(AccessError):
        assert channel_details_v1('user_1', channel_1)

    with pytest.raises(AccessError):
        assert channel_details_v1([1, 2, 3], channel_1)
    
    with pytest.raises(AccessError):
        assert channel_details_v1((1, 2, 3), channel_1)
