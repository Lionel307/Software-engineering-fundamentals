import pytest

from src.channels import channels_listall_v1, channels_create_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError, AccessError


@pytest.fixture
def get_auth_user_id():
    clear_v1()
    dict_auth_user_id = auth_register_v1('validemail@gmail.com', '123abc!@#', 'M', 'J')
    auth_user_id = dict_auth_user_id['auth_user_id'] 

    return auth_user_id


def test_no_channels(get_auth_user_id):    
    assert channels_listall_v1(get_auth_user_id) == {'channels': []}


def test_single_channel(get_auth_user_id):
    dict_channel_id = channels_create_v1(get_auth_user_id, 'channel 1', False)
    channel_id_1 = dict_channel_id['channel_id']

    expected_output = {
        'channels': [
        	{
        		'channel_id': channel_id_1,
        		'name': 'channel 1',
        	},
        ],
    }

    assert channels_listall_v1(get_auth_user_id) == expected_output


def test_multiple_channels(get_auth_user_id):
    dict_channel_id_1 = channels_create_v1(get_auth_user_id, 'channel 1', False)
    dict_channel_id_2 = channels_create_v1(get_auth_user_id, 'channel 2', False)
    dict_channel_id_3 = channels_create_v1(get_auth_user_id, 'channel 3', False)

    channel_id_1 = dict_channel_id_1['channel_id']
    channel_id_2 = dict_channel_id_2['channel_id']
    channel_id_3 = dict_channel_id_3['channel_id']

    expected_output = {
        'channels': [
        	{
        		'channel_id': channel_id_1,
        		'name': 'channel 1',
        	},
            {
        		'channel_id': channel_id_2,
        		'name': 'channel 2',
        	},
            {
        		'channel_id': channel_id_3,
        		'name': 'channel 3',
        	},
        ],
    }
    
    assert channels_listall_v1(get_auth_user_id) == expected_output


def test_wrong_auth_user_id(get_auth_user_id):
    with pytest.raises(AccessError):
        assert channels_listall_v1(get_auth_user_id + 1)

    with pytest.raises(AccessError):
        assert channels_listall_v1(get_auth_user_id + 2)

    with pytest.raises(AccessError):
        assert channels_listall_v1(get_auth_user_id - 1)


def test_invalid_auth_user_id():
    with pytest.raises(AccessError):
        assert channels_listall_v1('invalid id')

    with pytest.raises(AccessError):
        assert channels_listall_v1([1, 2, 3])

    with pytest.raises(AccessError):
        assert channels_listall_v1((1, 2, 3))

    with pytest.raises(AccessError):
        assert channels_listall_v1('1')
