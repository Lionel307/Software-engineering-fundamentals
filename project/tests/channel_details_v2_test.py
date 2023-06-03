import pytest

from src.channel import channel_details_v2, channel_join_v2
from src.channels import channels_create_v2
from src.auth import auth_register_v2
from src.other import clear_v1
from src.error import InputError, AccessError


@pytest.fixture
def user_1():
    clear_v1()
    user_1_dict = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    # token_1 = dict_auth_user_id_1['token'] 

    return user_1_dict


@pytest.fixture
def user_2():
    user_2_dict = auth_register_v2('another.email@gmail.com', '5823afc!@#', 'A', 'I')    
    # token_2 = dict_auth_user_id_2['token'] 

    return user_2_dict


@pytest.fixture
def channel_1(user_1):
    dict_channel_id = channels_create_v2(user_1["token"], "user 1's channel", True)
    channel_id = dict_channel_id['channel_id']

    return channel_id


def test_one_member(user_1, channel_1):
    expected_output = {
        'name': "user 1's channel",
        'is_public': True,
        'owner_members': [
            {
                'u_id': user_1["auth_user_id"],
                'email': 'validemail@gmail.com',
                'name_first': 'M',
                'name_last': 'J',
                'handle_str': 'mj'
            },
        ],
        'all_members': [
            {
                'u_id': user_1["auth_user_id"],
                'email': 'validemail@gmail.com',
                'name_first': 'M',
                'name_last': 'J',
                'handle_str': 'mj'
            },
        ],
    }

    assert channel_details_v2(user_1["token"], channel_1) == expected_output


def test_multiple_members(user_1, user_2, channel_1):
    channel_join_v2(user_2["token"], channel_1)

    expected_output = {
        'name': "user 1's channel",
        'is_public': True,
        'owner_members': [
            {
                'u_id': user_1["auth_user_id"],
                'email': 'validemail@gmail.com',
                'name_first': 'M',
                'name_last': 'J',
                'handle_str': 'mj'
            },
        ],
        'all_members': [
            {
                'u_id': user_1["auth_user_id"],
                'email': 'validemail@gmail.com',
                'name_first': 'M',
                'name_last': 'J',
                'handle_str': 'mj'
            },
            {
                'u_id': user_2["auth_user_id"],
                'email': 'another.email@gmail.com',
                'name_first': 'A',
                'name_last': 'I',
                'handle_str': 'ai'
            },
        ],
    }

    assert channel_details_v2(user_1["token"], channel_1) == expected_output
    assert channel_details_v2(user_2["token"], channel_1) == expected_output


def test_invalid_channel(user_1):
    with pytest.raises(InputError):
        channel_details_v2(user_1["token"], 'channel 1')

    with pytest.raises(InputError):
        channel_details_v2(user_1["token"], 1)

    with pytest.raises(InputError):
        channel_details_v2(user_1["token"], {'channel_id': 1})


def test_user_not_member(channel_1, user_2):
    with pytest.raises(AccessError):
        channel_details_v2(user_2["token"], channel_1)


def test_invalid_token(user_1, channel_1):
    with pytest.raises(AccessError):
        channel_details_v2({'user_1': 1}, channel_1)

    with pytest.raises(AccessError):
        channel_details_v2('user_1', channel_1)

    with pytest.raises(AccessError):
        channel_details_v2([1, 2, 3], channel_1)
    
    with pytest.raises(AccessError):
        channel_details_v2((1, 2, 3), channel_1)
    
    clear_v1()
