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

    user_3 = requests.post(url + "auth/register/v2", json={
        "email": "random@gmail.com", "password": "123abc!@#", 
        "name_first": "R", "name_last": "N"
    })
    user_3 = user_3.json()

    list_users = [user_1, user_2, user_3]

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
        "token": users[2]['token'], "name": "user 3's channel", "is_public": True
    })
    channel_3 = channel_3.json()
    channel_id_3 = channel_3["channel_id"]

    private_channel = requests.post(url + "channels/create/v2", json={
        "token": users[2]['token'], "name": "private channel", "is_public": False
    })
    private_channel = private_channel.json()
    private_channel_id = private_channel["channel_id"]

    dict_of_ids = {
        '1': channel_id_1,
        '2': channel_id_2,
        '3': channel_id_3,
        'private': private_channel_id,

    }

    return dict_of_ids


def test_correct_return(users, channel_ids):
    '''
    A test which checks that the return value of the route is correct
    '''
    payload = requests.post(url + "channel/join/v2", json={
        "token": users[0]['token'], "channel_id": channel_ids['2']
    })
    payload = payload.json()

    assert payload == {}


def test_joined_successfully(users, channel_ids):
    '''
    A test which checks if users can successfully join public channels
    '''
    # user 1 joining other channels
    requests.post(url + "channel/join/v2", json={
        "token": users[0]['token'], "channel_id": channel_ids['2']
    })
    requests.post(url + "channel/join/v2", json={
        "token": users[0]['token'], "channel_id": channel_ids['3']
    })
    # user 2 joining other channels
    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channel_ids['1']
    })
    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channel_ids['3']
    })
    # user 3 joining other channels
    requests.post(url + "channel/join/v2", json={
        "token": users[2]['token'], "channel_id": channel_ids['1']
    })
    requests.post(url + "channel/join/v2", json={
        "token": users[2]['token'], "channel_id": channel_ids['2']
    })

    # details of channel 1
    c_details_1 = requests.get(url + "channel/details/v2", params={
        "token": users[0]['token'], "channel_id": channel_ids['1']
    })
    c_details_1 = c_details_1.json()
    channel_1_members = c_details_1["all_members"]

    join_successful = []

    user_2_found_in_channel_1 = False
    user_3_found_in_channel_1 = False
    for member in channel_1_members:
        if member["u_id"] == users[1]["auth_user_id"]:
            user_2_found_in_channel_1 = True
        
        if member["u_id"] == users[2]["auth_user_id"]:
            user_3_found_in_channel_1 = True

    join_successful.append(user_2_found_in_channel_1)
    join_successful.append(user_3_found_in_channel_1)

    # details of channel 2
    c_details_2 = requests.get(url + "channel/details/v2", params={
        "token": users[1]['token'], "channel_id": channel_ids['2']
    })
    c_details_2 = c_details_2.json()
    channel_2_members = c_details_2["all_members"]

    user_1_found_in_channel_2 = False
    user_3_found_in_channel_2 = False
    for member in channel_2_members:
        if member["u_id"] == users[0]["auth_user_id"]:
            user_1_found_in_channel_2 = True
        
        if member["u_id"] == users[2]["auth_user_id"]:
            user_3_found_in_channel_2 = True

    join_successful.append(user_1_found_in_channel_2)
    join_successful.append(user_3_found_in_channel_2)

    # details of channel 3
    c_details_3 = requests.get(url + "channel/details/v2", params={
        "token": users[2]['token'], "channel_id": channel_ids['3']
    })
    c_details_3 = c_details_3.json()
    channel_3_members = c_details_3["all_members"]

    user_1_found_in_channel_3 = False
    user_2_found_in_channel_3 = False
    for member in channel_3_members:
        if member["u_id"] == users[0]["auth_user_id"]:
            user_1_found_in_channel_3 = True
        
        if member["u_id"] == users[1]["auth_user_id"]:
            user_2_found_in_channel_3 = True

    join_successful.append(user_1_found_in_channel_3)
    join_successful.append(user_2_found_in_channel_3)

    # assert that all boolean values are True, meaning users joined the channels successfully
    assert not False in join_successful


def test_global_owner(users, channel_ids):
    '''
    A test which checks if a Dreams (global) owner can successfully join a 
    private channel
    '''
    requests.post(url + "channel/join/v2", json={
        "token": users[0]['token'], "channel_id": channel_ids['private']
    })

    c_details = requests.get(url + "channel/details/v2", params={
        "token": users[0]['token'], "channel_id": channel_ids['private']
    })
    c_details = c_details.json()
    private_channel_members = c_details["all_members"]

    global_owner_found = False
    for member in private_channel_members:
        if member["u_id"] == users[0]["auth_user_id"]:
            global_owner_found = True

    assert global_owner_found == True


def test_invalid_channel(users):
    '''
    A test which checks if status code 400 is returned when the channel_id
    passed in is not a valid channel
    '''
    assert requests.post(url + "channel/join/v2", json={
        "token": users[0]['token'], "channel_id": 1
    }).status_code == 400

    assert requests.post(url + "channel/join/v2", json={
        "token": users[0]['token'], "channel_id": 'channel 1'
    }).status_code == 400

    assert requests.post(url + "channel/join/v2", json={
        "token": users[0]['token'], "channel_id": {'channel_id': 1}
    }).status_code == 400


def test_private_channel(users, channel_ids):
    '''
    A test which checks if status code 403 is returned when a user, who is
    not a Dreams owner tries to join a private channel
    '''
    assert requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channel_ids['private']
    }).status_code == 403


def test_invalid_token(channel_ids):
    '''
    A test which checks if status code 403 is returned when the token passed in
    is not a valid id
    '''
    assert requests.post(url + "channel/join/v2", json={
        "token": "invalid token", "channel_id": channel_ids['1']
    }).status_code == 403

    assert requests.post(url + "channel/join/v2", json={
        "token": 1, "channel_id": channel_ids['1']
    }).status_code == 403

    assert requests.post(url + "channel/join/v2", json={
        "token": [1, 2, 3], "channel_id": channel_ids['1']
    }).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
