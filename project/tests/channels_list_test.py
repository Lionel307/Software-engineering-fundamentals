import pytest

from src.channels import channels_list_v1, channels_create_v1
from src.channel import channel_invite_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError, AccessError


@pytest.fixture
def get_auth_user_id_1():
    clear_v1()
    dict_auth_user_id_1 = auth_register_v1('validemail@gmail.com', '123abc!@#', 'M', 'J')
    auth_user_id_1 = dict_auth_user_id_1['auth_user_id']

    return auth_user_id_1


@pytest.fixture
def get_auth_user_id_2():
    dict_auth_user_id_2 = auth_register_v1('anotherEmail@gmail.com', '5823afc!@#', 'A', 'I')
    auth_user_id_2 = dict_auth_user_id_2['auth_user_id'] 

    return auth_user_id_2


@pytest.fixture
def create_channels(get_auth_user_id_1, get_auth_user_id_2):
    dict_channel_id_1 = channels_create_v1(get_auth_user_id_1, "user 1's channel", True)
    dict_channel_id_2 = channels_create_v1(get_auth_user_id_2, "user 2's channel", True)
    dict_channel_id_3 = channels_create_v1(get_auth_user_id_2, "user 2's channel", True)

    channel_ids = []
    channel_ids.append(dict_channel_id_1['channel_id'])
    channel_ids.append(dict_channel_id_2['channel_id'])
    channel_ids.append(dict_channel_id_3['channel_id'])

    return channel_ids


def test_no_channels(get_auth_user_id_1):    
    assert channels_list_v1(get_auth_user_id_1) == {'channels': []}


def test_single_channel(get_auth_user_id_1):
    dict_channel_id = channels_create_v1(get_auth_user_id_1, 'channel 1', False)
    channel_id_1 = dict_channel_id['channel_id']

    expected_output = {
        'channels': [
        	{
        		'channel_id': channel_id_1,
        		'name': 'channel 1',
        	},
        ],
    }

    assert channels_list_v1(get_auth_user_id_1) == expected_output    


def test_multiple_users(get_auth_user_id_1, get_auth_user_id_2, create_channels):
    print(create_channels)
    expected_output_1 = {
        'channels': [
        	{
        		'channel_id': create_channels[0],
        		'name': "user 1's channel",
        	},
        ],
    }

    expected_output_2 = {
        'channels': [
        	{
        		'channel_id': create_channels[1],
        		'name': "user 2's channel",
        	},
            {
        		'channel_id': create_channels[2],
        		'name': "user 2's channel",
        	},
        ],
    }

    assert channels_list_v1(get_auth_user_id_1) == expected_output_1
    assert channels_list_v1(get_auth_user_id_2) == expected_output_2


def test_after_channel_invite(get_auth_user_id_1, get_auth_user_id_2, create_channels):
    channel_invite_v1(get_auth_user_id_2, create_channels[1], get_auth_user_id_1)
    channel_invite_v1(get_auth_user_id_2, create_channels[2], get_auth_user_id_1)

    expected_output = {
        'channels': [
        	{
        		'channel_id': create_channels[0],
        		'name': "user 1's channel",
        	},
            {
        		'channel_id': create_channels[1],
        		'name': "user 2's channel",
        	},
            {
        		'channel_id': create_channels[2],
        		'name': "user 2's channel",
        	},
        ],
    }

    assert channels_list_v1(get_auth_user_id_1) == expected_output


def test_wrong_auth_user_id(get_auth_user_id_1):
    clear_v1()

    with pytest.raises(AccessError):
        assert channels_list_v1(get_auth_user_id_1 + 1)

    with pytest.raises(AccessError):
        assert channels_list_v1(get_auth_user_id_1 + 2)

    with pytest.raises(AccessError):
        assert channels_list_v1(get_auth_user_id_1 + 3)


def test_invalid_auth_user_id():
    with pytest.raises(AccessError):
        assert channels_list_v1('invalid id')

    with pytest.raises(AccessError):
        assert channels_list_v1([1, 2, 3])

    with pytest.raises(AccessError):
        assert channels_list_v1((1, 2, 3))

    with pytest.raises(AccessError):
        assert channels_list_v1('1')
