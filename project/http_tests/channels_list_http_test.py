import pytest
import requests
import json

from src.config import url


@pytest.fixture
def users():
    '''
    Clears the database and registers users for use in tests
    '''
    requests.delete(url + "clear/v1")

    user_1 = requests.post(url + "auth/register/v2", json={
        "email": "validemail@gmail.com", "password": "123abc!@#", 
        "name_first": "M", "name_last": "J"
    })
    user_1 = user_1.json()

    user_2 = requests.post(url + "auth/register/v2", json={
        "email": "another.email@gmail.com", "password": "123abc!@#", 
        "name_first": "A", "name_last": "I"
    })
    user_2 = user_2.json()

    list_users = [user_1, user_2]

    return list_users


@pytest.fixture
def channel_ids(users):
    '''
    Creates channels for use in tests
    '''
    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": "user 1's channel", "is_public": True
    })
    channel_1 = channel_1.json()
    channel_id_1 = channel_1["channel_id"]

    channel_2 = requests.post(url + "channels/create/v2", json={
        "token": users[1]['token'], "name": "user 2's channel", "is_public": True
    })
    channel_2 = channel_2.json()
    channel_id_2 = channel_2["channel_id"]

    channel_3 = requests.post(url + "channels/create/v2", json={
        "token": users[1]['token'], "name": "user 2's 2nd channel", "is_public": True
    })
    channel_3 = channel_3.json()
    channel_id_3 = channel_3["channel_id"]

    list_ids = [channel_id_1, channel_id_2, channel_id_3]

    return list_ids


def test_success(users, channel_ids):
    '''
    A test which checks if channels_list successfully returns a list of channels
    which the user is part of
    '''
    requests.post(url + "channel/join/v2", json={
        "token": users[0]['token'], "channel_id": channel_ids[2]
    })

    expected_output = {
        'channels': [
        	{
        		'channel_id': channel_ids[0],
        		'name': "user 1's channel",
        	},
            {
        		'channel_id': channel_ids[2],
        		'name': "user 2's 2nd channel",
        	},
        ],
    }

    resp = requests.get(url + "channels/list/v2", params={"token": users[0]['token']})
    list_channels = resp.json()

    assert list_channels == expected_output


def test_invalid_token():
    '''
    A test which checks if status code 403 is returned when an invalid 
    token is passed in
    '''
    assert requests.get(
        url + "channels/list/v2", params={"token": "invalid token"}
    ).status_code == 403

    assert requests.get(
        url + "channels/list/v2", params={"token": 1}
    ).status_code == 403

    assert requests.get(
        url + "channels/list/v2", params={"token": [1, 2, 3]}
    ).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
