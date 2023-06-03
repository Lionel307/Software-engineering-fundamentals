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
        "email": "validemail@gmail.com", "password": "abcdefgh", 
        "name_first": "M", "name_last": "J"
    })
    user_1 = user_1.json()
    
    user_2 = requests.post(url + "auth/register/v2", json={
        "email": "anotheremail@gmail.com", "password": "abcdefgh", 
        "name_first": "A", "name_last": "I"
    })
    user_2 = user_2.json()

    user_3 = requests.post(url + "auth/register/v2", json={
        "email": "random@gmail.com", "password": "abcdefgh", 
        "name_first": "R", "name_last": "N"
    })
    user_3 = user_3.json()
    
    list_users = [user_1, user_2, user_3]

    return list_users


@pytest.fixture
def dm_id_1(users):
    '''
    Creates a dm for use in tests
    '''
    dm_1 = requests.post(url + "dm/create/v1", json={
        "token": users[0]["token"], "u_ids": [users[1]["auth_user_id"]]
    })
    dm_1 = dm_1.json()

    return dm_1["dm_id"]


@pytest.fixture
def dm_id_2(users):
    '''
    Creates a dm for use in tests
    '''
    dm_2 = requests.post(url + "dm/create/v1", json={
        "token": users[0]["token"], 
        "u_ids": [users[1]["auth_user_id"], users[2]["auth_user_id"]]
    })
    dm_2 = dm_2.json()

    return dm_2["dm_id"]


def test_correct_return(users, dm_id_1):
    '''
    A test which checks if the return value of the route is correct
    '''
    output = requests.delete(url + "dm/remove/v1", json={
        "token": users[0]["token"], "dm_id": dm_id_1
    })
    output = output.json()

    assert output == {}


def test_removed_successfully(users, dm_id_1, dm_id_2):
    '''
    A test which checks if a dm is successfully removed and other dms are unchanged
    '''
    requests.delete(url + "dm/remove/v1", json={
        "token": users[0]["token"], "dm_id": dm_id_1
    })

    resp = requests.get(url + "dm/list/v1", params={
        "token": users[0]["token"]
    })
    payload = resp.json()
    list_dms = payload["dms"]
    
    dm_removed = True
    other_dm_present = False
    for dm in list_dms:
        if dm["dm_id"] == dm_id_1:
            dm_removed = False
        if dm["dm_id"] == dm_id_2:
            other_dm_present = True

    assert dm_removed == True and other_dm_present == True


def test_invalid_dm(users, dm_id_1):
    '''
    A test which checks if status code 400 is raised when dm_id is not a valid dm
    '''
    assert requests.delete(url + "dm/remove/v1", json={
        "token": users[0]['token'], "dm_id": dm_id_1 + 1
    }).status_code == 400

    assert requests.delete(url + "dm/remove/v1", json={
        "token": users[0]['token'], "dm_id": dm_id_1 + 2
    }).status_code == 400

    assert requests.delete(url + "dm/remove/v1", json={
        "token": users[0]['token'], "dm_id": dm_id_1 + 3
    }).status_code == 400


def test_not_creator(users, dm_id_1, dm_id_2):
    '''
    A test which checks if status code 403 is returned when the user trying to remove a dm
    is not the original creator of the dm
    '''
    assert requests.delete(url + "dm/remove/v1", json={
        "token": users[1]['token'], "dm_id": dm_id_1
    }).status_code == 403

    assert requests.delete(url + "dm/remove/v1", json={
        "token": users[1]['token'], "dm_id": dm_id_2
    }).status_code == 403

    assert requests.delete(url + "dm/remove/v1", json={
        "token": users[2]['token'], "dm_id": dm_id_1
    }).status_code == 403


def test_invalid_token(users, dm_id_1):
    '''
    A test which checks if status code 403 is returned when the token passed in
    is not a valid id
    '''
    # invalidates the token of user 1
    requests.post(url + "auth/logout/v1", json={"token": users[0]["token"]})

    assert requests.delete(
        url + "dm/remove/v1", json={"token": users[0]["token"], "dm_id": dm_id_1
    }).status_code == 403

    assert requests.delete(
        url + "dm/remove/v1", json={"token": "invalid token", "dm_id": dm_id_1
    }).status_code == 403

    assert requests.delete(
        url + "dm/remove/v1", json={"token": 1, "dm_id": dm_id_1
    }).status_code == 403

    assert requests.delete(
        url + "dm/remove/v1", json={"token": [1, 2, 3], "dm_id": dm_id_1
    }).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
