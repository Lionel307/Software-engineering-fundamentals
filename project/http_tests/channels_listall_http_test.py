import pytest
import requests
import json

from src.config import url


@pytest.fixture
def get_user():
    '''
    Clears the database and registers a user for use in tests
    '''
    requests.delete(url + "clear/v1")

    user_1 = requests.post(url + "auth/register/v2", json={
        "email": "validemail@gmail.com", "password": "123abc!@#", 
        "name_first": "Hayden", "name_last": "Everest"
    })
    user_1 = user_1.json()

    return user_1


@pytest.fixture
def channel_1(get_user):
    '''
    Creates a channel for use in tests
    '''
    channel = requests.post(url + "channels/create/v2", json={
        "token": get_user['token'], "name": "channel 1", "is_public": True
    })
    channel = channel.json()

    return channel


def test_correct_return_type(get_user):
    '''
    A test which checks that the return type for channels_listall_v2 is a dictionary
    '''
    list_channels = requests.get(url + "channels/listall/v2", params={"token": get_user['token']})
    list_channels = list_channels.json()

    assert isinstance(list_channels, dict) == True


def test_no_channels(get_user):
    '''
    A test which checks the output when there are no channels in Dreams
    '''
    list_channels = requests.get(url + "channels/listall/v2", params={"token": get_user['token']})
    list_channels = list_channels.json()

    assert list_channels == {'channels': []}


def test_single_channel(get_user):
    '''
    A test which checks the output when there is only 1 channel in Dreams
    '''
    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": get_user['token'], "name": "channel 1", "is_public": True
    })
    channel_1 = channel_1.json()
    channel_id_1 = channel_1["channel_id"]

    expected_output = {
        'channels': [
        	{
        		'channel_id': channel_id_1,
        		'name': 'channel 1',
        	},
        ],
    }

    list_channels = requests.get(url + "channels/listall/v2", params={"token": get_user['token']})
    list_channels = list_channels.json()

    assert list_channels == expected_output


def test_multiple_channels(get_user, channel_1):
    '''
    A test which checks the output when multiple channels exist in Dreams
    '''

    channel_id_1 = channel_1["channel_id"]

    channel_2 = requests.post(url + "channels/create/v2", json={
        "token": get_user['token'], "name": "channel 2", "is_public": True
    })
    channel_2 = channel_2.json()
    channel_id_2 = channel_2["channel_id"]

    channel_3 = requests.post(url + "channels/create/v2", json={
        "token": get_user['token'], "name": "channel 3", "is_public": True
    })
    channel_3 = channel_3.json()
    channel_id_3 = channel_3["channel_id"]

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
    
    list_channels = requests.get(url + "channels/listall/v2", params={"token": get_user['token']})
    list_channels = list_channels.json()

    assert list_channels == expected_output


def test_invalid_token():
    '''
    A test which checks if status code 403 is returned when an invalid 
    token is passed in
    '''
    assert requests.get(
        url + "channels/listall/v2", params={"token": "invalid token"}
    ).status_code == 403

    assert requests.get(
        url + "channels/listall/v2", params={"token": 1}
    ).status_code == 403

    assert requests.get(
        url + "channels/listall/v2", params={"token": [1, 2, 3]}
    ).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
