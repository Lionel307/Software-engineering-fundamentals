import pytest
import requests
import json

from src.config import url


@pytest.fixture
def user_1():
    '''
    Clears the database and registers user 1 for use in tests
    '''
    requests.delete(url + "clear/v1")

    user = requests.post(url + "auth/register/v2", json={
        "email": "validemail@gmail.com", "password": "123abc!@#", 
        "name_first": "M", "name_last": "J"
    })
    user = user.json()

    return user


@pytest.fixture
def user_2():
    '''
    Registers user 2 for use in tests
    '''
    user = requests.post(url + "auth/register/v2", json={
        "email": "another.email@gmail.com", "password": "123abc!@#", 
        "name_first": "A", "name_last": "I"
    })
    user = user.json()

    return user


@pytest.fixture
def channel_1_id(user_1):
    '''
    Creates a channel for use in tests
    '''
    channel = requests.post(url + "channels/create/v2", json={
        "token": user_1['token'], "name": "user 1's channel", "is_public": True
    })
    channel = channel.json()
    channel_id = channel["channel_id"]

    return channel_id


def test_correct_return_type(user_1, channel_1_id):
    '''
    A test which checks that the return type for the route is a dictionary
    '''
    c_details = requests.get(url + "channel/details/v2", params={
        "token": user_1['token'], "channel_id": channel_1_id
    })
    c_details = c_details.json()

    assert isinstance(c_details, dict) == True


def test_one_member(user_1, channel_1_id):
    '''
    A test which checks the output when the channel has only one member
    '''
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
    
    c_details = requests.get(url + "channel/details/v2", params={
        "token": user_1['token'], "channel_id": channel_1_id
    })
    c_details = c_details.json()

    assert c_details == expected_output


def test_multiple_members(user_1, user_2, channel_1_id):
    '''
    A test which checks the output when multiple members are part of the channel
    '''
    requests.post(url + "channel/join/v2", json={
        "token": user_2['token'], "channel_id": channel_1_id
    })

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

    c_details_1 = requests.get(url + "channel/details/v2", params={
        "token": user_1['token'], "channel_id": channel_1_id
    })

    c_details_1 = c_details_1.json()

    c_details_2 = requests.get(url + "channel/details/v2", params={
        "token": user_2['token'], "channel_id": channel_1_id
    })

    c_details_2 = c_details_2.json()

    assert c_details_1 == expected_output and c_details_1 == c_details_2


def test_invalid_channel(user_1):
    '''
    A test which checks if status code 400 is returned when the channel_id
    passed in is not a valid channel
    '''
    assert requests.get(url + "channel/details/v2", params={
        "token": user_1['token'], "channel_id": 1
    }).status_code == 400

    assert requests.get(url + "channel/details/v2", params={
        "token": user_1['token'], "channel_id": 'channel 1'
    }).status_code == 400

    assert requests.get(url + "channel/details/v2", params={
        "token": user_1['token'], "channel_id": {'channel_id': 1}
    }).status_code == 400


def test_user_not_member(channel_1_id, user_2):
    '''
    A test which checks if status code 403 is returned when the authorised user
    is not a member of the channel with channel_id
    '''
    assert requests.get(url + "channel/details/v2", params={
        "token": user_2['token'], "channel_id": channel_1_id
    }).status_code == 403


def test_invalid_token(channel_1_id):
    '''
    A test which checks if status code 403 is returned when the token passed in
    is not a valid id
    '''
    assert requests.get(
        url + "channel/details/v2", params={"token": "invalid token", "channel_id": channel_1_id}
    ).status_code == 403

    assert requests.get(
        url + "channel/details/v2", params={"token": 1, "channel_id": channel_1_id}
    ).status_code == 403

    assert requests.get(
        url + "channel/details/v2", params={"token": [1, 2, 3], "channel_id": channel_1_id}
    ).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
