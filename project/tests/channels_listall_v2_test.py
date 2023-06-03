import pytest

from src.channels import channels_listall_v2, channels_create_v2
from src.auth import auth_register_v2
from src.other import clear_v1
from src.error import InputError, AccessError


@pytest.fixture
def get_user():
    '''
    Registers users for use in tests
    '''
    clear_v1()
    dict_user = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')

    return dict_user


def test_correct_return_type(get_user):
    '''
    A test which checks that the return type for channels_listall_v2 is a dictionary
    '''
    list_of_channels = channels_listall_v2(get_user['token'])
    assert isinstance(list_of_channels, dict) == True


def test_no_channels(get_user):
    '''
    A test which checks the output when there are no channels in Dreams
    '''
    assert channels_listall_v2(get_user['token']) == {'channels': []}


def test_single_channel(get_user):
    '''
    A test which checks the output when there is only 1 channel in Dreams
    '''
    dict_channel_id = channels_create_v2(get_user['token'], 'channel 1', False)
    channel_id_1 = dict_channel_id['channel_id']

    expected_output = {
        'channels': [
        	{
        		'channel_id': channel_id_1,
        		'name': 'channel 1',
        	},
        ],
    }

    assert channels_listall_v2(get_user['token']) == expected_output


def test_multiple_channels(get_user):
    '''
    A test which checks the output when multiple channels exist in Dreams
    '''
    dict_channel_id_1 = channels_create_v2(get_user['token'], 'channel 1', False)
    dict_channel_id_2 = channels_create_v2(get_user['token'], 'channel 2', False)
    dict_channel_id_3 = channels_create_v2(get_user['token'], 'channel 3', False)

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
    
    assert channels_listall_v2(get_user['token']) == expected_output


def test_invalid_auth_user_id():
    '''
    A test which checks if an AccessError is raised when the token passed in 
    is not a valid id
    '''
    with pytest.raises(AccessError):
        assert channels_listall_v2('')

    with pytest.raises(AccessError):
        assert channels_listall_v2('invalid token')

    with pytest.raises(AccessError):
        assert channels_listall_v2([1, 2, 3])

    with pytest.raises(AccessError):
        assert channels_listall_v2((1, 2, 3))

    with pytest.raises(AccessError):
        assert channels_listall_v2({})

    # To clear the persistent data file once all the tests have been executed
    clear_v1()