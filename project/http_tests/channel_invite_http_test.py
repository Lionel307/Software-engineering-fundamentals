import pytest
import requests
import json

from src.config import url


@pytest.fixture
def auth_user():
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
def invited_user():
    '''
    Registers the user who will be invited to a channel in tests
    '''
    user = requests.post(url + "auth/register/v2", json={
        "email": "another.email@gmail.com", "password": "123abc!@#", 
        "name_first": "A", "name_last": "I"
    })
    user = user.json()

    return user


@pytest.fixture
def channel_1_id(auth_user):
    '''
    Creates a channel for use in tests
    '''
    channel = requests.post(url + "channels/create/v2", json={
        "token": auth_user['token'], "name": "user 1's channel", "is_public": False
    })
    channel = channel.json()
    channel_id = channel["channel_id"]

    return channel_id


def test_valid_return(auth_user, invited_user, channel_1_id):
    '''
    A test which checks that the return value of the route is correct
    '''
    payload = requests.post(url + "channel/invite/v2", json={
        "token": auth_user["token"], "channel_id": channel_1_id, 
        "u_id": invited_user["auth_user_id"]
    })
    payload = payload.json()

    assert payload == {}


def test_successfully_joined(auth_user, invited_user, channel_1_id):
    '''
    A test which checks if a user who was invited to a channel 
    successfully joined it
    '''
    requests.post(url + "channel/invite/v2", json={
        "token": auth_user["token"], "channel_id": channel_1_id, 
        "u_id": invited_user["auth_user_id"]
    })

    resp = requests.get(url + "channels/list/v2", params={"token": invited_user['token']})
    list_channels = resp.json()
    list_channels = list_channels["channels"]

    is_member = False
    for channel in list_channels:
        if channel["channel_id"] == channel_1_id:
            is_member = True

    assert is_member == True


def test_invalid_channel(auth_user, invited_user):
    '''
    A test which checks if status code 400 is returned when the channel_id passed in 
    does not refer to a valid channel
    '''
    assert requests.post(url + "channel/invite/v2", json={
        "token": auth_user["token"], "channel_id": 7, 
        "u_id": invited_user["auth_user_id"]
    }).status_code == 400

    assert requests.post(url + "channel/invite/v2", json={
        "token": auth_user["token"], "channel_id": "invalid", 
        "u_id": invited_user["auth_user_id"]
    }).status_code == 400


def test_invalid_invited_user(auth_user, channel_1_id):
    '''
    A test which checks if status code 400 is returned when the u_id passed in 
    does not refer to a valid user
    '''
    assert requests.post(url + "channel/invite/v2", json={
        "token": auth_user["token"], "channel_id": channel_1_id, 
        "u_id": "invalid"
    }).status_code == 400

    assert requests.post(url + "channel/invite/v2", json={
        "token": auth_user["token"], "channel_id": channel_1_id, 
        "u_id": 8
    }).status_code == 400


def test_not_member(channel_1_id, invited_user):
    '''
    A test which checks if status code 403 is returned when the authorised user 
    is not a member of the channel with channel_id
    '''
    user = requests.post(url + "auth/register/v2", json={
        "email": "randomemail@gmail.com", "password": "123abc!@#", 
        "name_first": "R", "name_last": "N"
    })
    user = user.json()

    assert requests.post(url + "channel/invite/v2", json={
        "token": invited_user["token"], "channel_id": channel_1_id, 
        "u_id": user["auth_user_id"]
    }).status_code == 403


def test_invalid_token(channel_1_id, invited_user):
    '''
    A test which checks if status code 403 is returned when the token passed in
    is not a valid id
    '''
    assert requests.post(url + "channel/invite/v2", json={
        "token": "invalid token", "channel_id": channel_1_id,
        "u_id": invited_user["auth_user_id"]
    }).status_code == 403

    assert requests.post(url + "channel/invite/v2", json={
        "token": 1, "channel_id": channel_1_id,
        "u_id": invited_user["auth_user_id"]
    }).status_code == 403

    assert requests.post(url + "channel/invite/v2", json={
        "token": [1, 2, 3], "channel_id": channel_1_id,
        "u_id": invited_user["auth_user_id"]
    }).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
    