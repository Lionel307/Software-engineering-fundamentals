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


def test_correct_return(users, dm_id_1):
    '''
    A test which checks if the return value of the route is correct
    '''
    output = requests.post(url + "dm/invite/v1", json={
        "token": users[0]["token"], "dm_id": dm_id_1, "u_id": users[2]["auth_user_id"]
    })
    output = output.json()

    assert output == {}


def test_one_user_invited(users, dm_id_1):
    '''
    A test which checks if a user successfully got added to a dm after being invited to one
    '''
    requests.post(url + "dm/invite/v1", json={
        "token": users[0]["token"], "dm_id": dm_id_1, "u_id": users[2]["auth_user_id"]
    })

    resp = requests.get(url + "dm/list/v1", params={
        "token": users[2]["token"]
    })
    payload = resp.json()
    list_dms = payload["dms"]
    
    invited_to_dm = False
    for dm in list_dms:
        if dm["dm_id"] == dm_id_1:
            invited_to_dm = True

    assert invited_to_dm == True 


def test_invalid_dm(users, dm_id_1):
    '''
    A test which checks if status code 400 is raised when dm_id is not a valid dm
    '''
    assert requests.post(url + "dm/invite/v1", json={
        "token": users[0]['token'], "dm_id": dm_id_1 + 1, "u_id": users[2]["auth_user_id"]
    }).status_code == 400

    assert requests.post(url + "dm/invite/v1", json={
        "token": users[0]['token'], "dm_id": dm_id_1 + 2, "u_id": users[2]["auth_user_id"]
    }).status_code == 400

    assert requests.post(url + "dm/invite/v1", json={
        "token": users[0]['token'], "dm_id": dm_id_1 + 3, "u_id": users[2]["auth_user_id"]
    }).status_code == 400


def test_invalid_u_id(users, dm_id_1):
    '''
    A test which checks if status code 400 is raised when dm_id is not a valid dm
    '''
    assert requests.post(url + "dm/invite/v1", json={
        "token": users[0]['token'], "dm_id": dm_id_1, "u_id": users[2]["auth_user_id"] + 1
    }).status_code == 400

    assert requests.post(url + "dm/invite/v1", json={
        "token": users[0]['token'], "dm_id": dm_id_1, "u_id": users[2]["auth_user_id"] + 2
    }).status_code == 400

    assert requests.post(url + "dm/invite/v1", json={
        "token": users[0]['token'], "dm_id": dm_id_1, "u_id": users[2]["auth_user_id"] + 3
    }).status_code == 400


def test_auth_not_member(users, dm_id_1):
    '''
    A test which checks if status code 403 is returned when the authorised user
    is not a member of the dm with dm_id
    '''
    new_user = requests.post(url + "auth/register/v2", json={
        "email": "new.email@gmail.com", "password": "abcdefgh", 
        "name_first": "N", "name_last": "E"
    })
    new_user = new_user.json()

    assert requests.post(url + "dm/invite/v1", json={
        "token": new_user['token'], "dm_id": dm_id_1, "u_id": users[2]["auth_user_id"]
    }).status_code == 403


def test_invalid_token(users, dm_id_1):
    '''
    A test which checks if status code 403 is returned when the token passed in
    is not a valid id
    '''
    # invalidates the token of user 1
    requests.post(url + "auth/logout/v1", json={"token": users[0]["token"]})

    assert requests.post(url + "dm/invite/v1", json={
        "token": users[0]["token"], "dm_id": dm_id_1, "u_id": users[2]["auth_user_id"]
    }).status_code == 403

    assert requests.post(url + "dm/invite/v1", json={
        "token": "invalid token", "dm_id": dm_id_1, "u_id": users[2]["auth_user_id"]
    }).status_code == 403

    assert requests.post(url + "dm/invite/v1", json={
        "token": 1, "dm_id": dm_id_1, "u_id": users[2]["auth_user_id"]
    }).status_code == 403

    assert requests.post(url + "dm/invite/v1", json={
        "token": [1, 2, 3], "dm_id": dm_id_1, "u_id": users[2]["auth_user_id"]
    }).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
