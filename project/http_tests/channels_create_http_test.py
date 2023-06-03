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
        "email": "hi@hi.com", "password": "abcdefgh", 
        "name_first": "Hayden", "name_last": "Smith"
    })
    user_1 = user_1.json()
    
    user_2 = requests.post(url + "auth/register/v2", json={
        "email": "hi2@hi.com", "password": "abcdefgh", 
        "name_first": "Nothayden", "name_last": "Smith"
    })
    user_2 = user_2.json()
    
    list_users = [user_1, user_2]

    return list_users


def test_correct_return_type(users):
    '''
    A test which checks that the return value and the channel_id are of
    the correct type
    '''
    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": "test", "is_public": True
    })

    channel_1 = channel_1.json()

    assert isinstance(channel_1, dict) == True
    assert isinstance(channel_1["channel_id"], int) == True


def test_channel_created(users):
    '''
    A test which checks if a channel was successfully created
    '''
    NAME = "test"    

    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": NAME, "is_public": True
    })
    channel_1 = channel_1.json()

    list_channels = requests.get(url + "channels/listall/v2", params={"token": users[0]['token']})
    list_channels = list_channels.json()["channels"]

    assert list_channels[0]["channel_id"] == channel_1["channel_id"] and \
           list_channels[0]["name"] == NAME


def test_multiple_channels(users):
    '''
    A test which checks if multiple channels can be successfully created
    '''
    NAME_1 = "test"
    NAME_2 = "hello"

    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": NAME_1, "is_public": True
    })
    channel_1 = channel_1.json()

    channel_2 = requests.post(url + "channels/create/v2", json={
        "token": users[1]['token'], "name": NAME_2, "is_public": True
    })
    channel_2 = channel_2.json()


    list_channels = requests.get(url + "channels/listall/v2", params={"token": users[0]['token']})
    list_channels = list_channels.json()["channels"]

    channel_1_created = False
    for channel in list_channels:
        if channel["channel_id"] == channel_1["channel_id"] and channel["name"] == NAME_1:
            channel_1_created = True

    channel_2_created = False
    for channel in list_channels:
        if channel["channel_id"] == channel_2["channel_id"] and channel["name"] == NAME_2:
            channel_2_created = True

    assert channel_1_created == True and channel_2_created == True


def test_invalid_name(users):
    '''
    A test which checks if status code 400 is returned when the channel name
    passed in is more than 20 characters long
    '''
    assert requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": "abcdefghijklmnopqrstuvw", "is_public": True
    }).status_code == 400

    assert requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": "123456789112345678911", "is_public": True
    }).status_code == 400


def test_invalid_token():
    '''
    A test which checks if status code 403 is returned when an invalid 
    token is passed in
    '''
    NAME_1 = "test"

    assert requests.post(url + "channels/create/v2", json={
        "token": "invalid_token", "name": NAME_1, "is_public": True
    }).status_code == 403

    assert requests.post(url + "channels/create/v2", json={
        "token": [1, 2, 3], "name": NAME_1, "is_public": True
    }).status_code == 403


    assert requests.post(url + "channels/create/v2", json={
        "token": 1, "name": NAME_1, "is_public": True
    }).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
