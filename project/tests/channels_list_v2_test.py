import pytest

from src.channels import channels_list_v2, channels_create_v2
from src.channel import channel_join_v2
from src.auth import auth_register_v2, auth_logout_v1
from src.other import clear_v1
from src.error import InputError, AccessError


@pytest.fixture
def get_user_1():
    '''
    Registers user 1 for use in tests
    '''
    clear_v1()
    user_1 = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')

    return user_1


@pytest.fixture
def get_user_2():
    '''
    Registers user 2 for use in tests
    '''
    user_2 = auth_register_v2('anotherEmail@gmail.com', '5823afc!@#', 'A', 'I')

    return user_2


@pytest.fixture
def create_channels(get_user_1, get_user_2):
    '''
    Creates channels for use in tests
    '''
    dict_channel_id_1 = channels_create_v2(get_user_1['token'], "user 1's channel", True)
    dict_channel_id_2 = channels_create_v2(get_user_2['token'], "user 2's channel", True)
    dict_channel_id_3 = channels_create_v2(get_user_2['token'], "user 2's channel", True)

    channel_ids = []
    channel_ids.append(dict_channel_id_1['channel_id'])
    channel_ids.append(dict_channel_id_2['channel_id'])
    channel_ids.append(dict_channel_id_3['channel_id'])

    return channel_ids


def test_correct_return_type(get_user_1):
    '''
    A test which checks that the return type for channels_list_v2 is a dictionary
    '''
    list_of_channels = channels_list_v2(get_user_1['token'])
    assert isinstance(list_of_channels, dict) == True


def test_no_channels(get_user_1):
    '''
    A test which checks the output when there are no channels
    '''
    assert channels_list_v2(get_user_1['token']) == {'channels': []}


def test_single_channel(get_user_1):
    '''
    A test which checks the output when there is only 1 channel
    '''
    dict_channel_id = channels_create_v2(get_user_1['token'], 'channel 1', False)
    channel_id_1 = dict_channel_id['channel_id']

    expected_output = {
        'channels': [
        	{
        		'channel_id': channel_id_1,
        		'name': 'channel 1',
        	},
        ],
    }

    assert channels_list_v2(get_user_1['token']) == expected_output    


def test_multiple_users(get_user_1, get_user_2, create_channels):
    '''
    A test which checks the output for multiple users
    '''
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

    assert channels_list_v2(get_user_1['token']) == expected_output_1
    assert channels_list_v2(get_user_2['token']) == expected_output_2


def test_after_channel_join(get_user_1, get_user_2, create_channels):
    '''
    A test which checks the output after a user joins a new channel 
    '''
    channel_join_v2(get_user_1['token'], create_channels[1])
    channel_join_v2(get_user_1['token'], create_channels[2])

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

    assert channels_list_v2(get_user_1['token']) == expected_output


def test_invalid_token(get_user_1):
    '''
    A test which checks if an AccessError is raised when the token passed in 
    is not valid
    '''
    # invalidates token of user 1
    auth_logout_v1(get_user_1['token'])

    with pytest.raises(AccessError):
        assert channels_list_v2(get_user_1['token'])

    with pytest.raises(AccessError):
        assert channels_list_v2('')

    with pytest.raises(AccessError):
        assert channels_list_v2('invalid token')

    with pytest.raises(AccessError):
        assert channels_list_v2({})

    # To clear the persistent data file once all the tests have been executed
    clear_v1()
