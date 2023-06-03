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

    list_ids = [channel_id_1, channel_id_2, channel_id_3]

    return list_ids


def test_correct_return(users, channel_ids):
    '''
    A test which checks if the return value of the route is correct
    '''
    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channel_ids[0]
    })

    requests.post(url + "channel/addowner/v1", json={
        "token": users[0]["token"], "channel_id": channel_ids[0],
        "u_id": users[1]["auth_user_id"]
    })

    payload = requests.post(url + "channel/removeowner/v1", json={
        "token": users[0]["token"], "channel_id": channel_ids[0],
        "u_id": users[1]["auth_user_id"]
    })

    payload = payload.json()

    assert payload == {}


def test_owner_removed(users, channel_ids):
    requests.post(url + "channel/join/v2", json={
        "token": users[0]['token'], "channel_id": channel_ids[2]
    })

    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channel_ids[2]
    })

    requests.post(url + "channel/addowner/v1", json={
        "token": users[0]["token"], "channel_id": channel_ids[2],
        "u_id": users[1]["auth_user_id"]
    })

    requests.post(url + "channel/removeowner/v1", json={
        "token": users[1]["token"], "channel_id": channel_ids[2],
        "u_id": users[2]["auth_user_id"]
    })

    c_details = requests.get(url + "channel/details/v2", params={
        "token": users[1]["token"], "channel_id": channel_ids[2],
    })
    c_details = c_details.json()
    list_owners = c_details["owner_members"]
    list_members = c_details["all_members"]

    owner_removed = True
    for owner in list_owners:
        if owner["u_id"] == users[2]["auth_user_id"]:
            owner_removed = False

    is_member = False
    for member in list_members:
        if member['u_id'] == users[2]["auth_user_id"]:
            is_member = True

    assert owner_removed == True and is_member == True


def test_invalid_channel(users):
    '''
    A test which checks if status code 400 is returned when the channel_id
    passed in is not a valid channel
    '''
    assert requests.post(url + "channel/removeowner/v1", json={
        "token": users[0]['token'], "channel_id": 1,
        "u_id": users[1]
    }).status_code == 400

    assert requests.post(url + "channel/removeowner/v1", json={
        "token": users[0]['token'], "channel_id": 'channel 1',
        "u_id": users[1]
    }).status_code == 400

    assert requests.post(url + "channel/removeowner/v1", json={
        "token": users[0]['token'], "channel_id": {'channel_id': 1},
        "u_id": users[1]
    }).status_code == 400


def test_user_not_owner(users, channel_ids):
    '''
    A test which checks if status code 400 is returned when the user with u_id
    is not an owner of the channel
    '''
    requests.post(url + "channel/join/v2", json={
        "token": users[0]['token'], "channel_id": channel_ids[2]
    })

    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channel_ids[2]
    })
    
    assert requests.post(url + "channel/removeowner/v1", json={
        "token": users[2]["token"], "channel_id": channel_ids[2],
        "u_id": users[0]["auth_user_id"]
    }).status_code == 400

    assert requests.post(url + "channel/removeowner/v1", json={
        "token": users[2]["token"], "channel_id": channel_ids[2],
        "u_id": users[1]["auth_user_id"]
    }).status_code == 400


def test_only_owner(users, channel_ids):
    '''
    A test which checks if status code 400 is returned when the user is the only
    owner of the channel
    '''
    assert requests.post(url + "channel/removeowner/v1", json={
        "token": users[0]["token"], "channel_id": channel_ids[0],
        "u_id": users[0]["auth_user_id"]
    }).status_code == 400

    assert requests.post(url + "channel/removeowner/v1", json={
        "token": users[1]["token"], "channel_id": channel_ids[1],
        "u_id": users[1]["auth_user_id"]
    }).status_code == 400

    assert requests.post(url + "channel/removeowner/v1", json={
        "token": users[2]["token"], "channel_id": channel_ids[2],
        "u_id": users[2]["auth_user_id"]
    }).status_code == 400


def test_auth_not_owner(users, channel_ids):
    '''
    A test which checks if status code 403 is returned when the authorised user
    is not an owner of Dreams, or an owner of the channel
    '''
    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channel_ids[0]
    })

    requests.post(url + "channel/join/v2", json={
        "token": users[2]['token'], "channel_id": channel_ids[1]
    })

    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channel_ids[2]
    })

    assert requests.post(url + "channel/removeowner/v1", json={
        "token": users[1]["token"], "channel_id": channel_ids[0],
        "u_id": users[0]["auth_user_id"]
    }).status_code == 403

    assert requests.post(url + "channel/removeowner/v1", json={
        "token": users[2]["token"], "channel_id": channel_ids[1],
        "u_id": users[1]["auth_user_id"]
    }).status_code == 403

    assert requests.post(url + "channel/removeowner/v1", json={
        "token": users[1]["token"], "channel_id": channel_ids[2],
        "u_id": users[2]["auth_user_id"]
    }).status_code == 403


def test_invalid_token(users, channel_ids):
    '''
    A test which checks if status code 403 is returned when the token passed in
    is not a valid id
    '''
    assert requests.post(url + "channel/removeowner/v1", json={
        "token": "invalid token", "channel_id": channel_ids[0],
        "u_id": users[1]
    }).status_code == 403

    assert requests.post(url + "channel/removeowner/v1", json={
        "token": 1, "channel_id": channel_ids[0],
        "u_id": users[1]
    }).status_code == 403

    assert requests.post(url + "channel/removeowner/v1", json={
        "token": [1, 2, 3], "channel_id": channel_ids[0],
        "u_id": users[1]
    }).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
