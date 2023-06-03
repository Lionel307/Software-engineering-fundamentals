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
def dm_1(users):
    '''
    Creates a dm for use in tests
    '''
    dm_1 = requests.post(url + "dm/create/v1", json={
        "token": users[0]["token"], 
        "u_ids": [users[1]["auth_user_id"], users[2]["auth_user_id"]]})
    dm_1 = dm_1.json()

    return dm_1


def test_correct_return(users, dm_1):
    '''
    A test which checks that the route returns the correct information
    '''
    expected_output = {
        'name': dm_1["dm_name"],
        'members': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'validemail@gmail.com',
                'name_first': 'M',
                'name_last': 'J',
                'handle_str': 'mj'
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'anotheremail@gmail.com',
                'name_first': 'A',
                'name_last': 'I',
                'handle_str': 'ai'
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'random@gmail.com',
                'name_first': 'R',
                'name_last': 'N',
                'handle_str': 'rn'
            },
        ],
    }

    d_details_1 = requests.get(url + "dm/details/v1", params={
        "token": users[0]['token'], "dm_id": dm_1["dm_id"]
    })
    d_details_1 = d_details_1.json()

    d_details_2 = requests.get(url + "dm/details/v1", params={
        "token": users[1]['token'], "dm_id": dm_1["dm_id"]
    })
    d_details_2 = d_details_2.json()

    d_details_3 = requests.get(url + "dm/details/v1", params={
        "token": users[2]['token'], "dm_id": dm_1["dm_id"]
    })
    d_details_3 = d_details_3.json()

    assert d_details_1 == expected_output
    assert d_details_2 == expected_output
    assert d_details_3 == expected_output


def test_invalid_dm(users, dm_1):
    '''
    A test which checks if status code 400 is raised when dm_id is not a valid dm
    '''
    assert requests.get(url + "dm/details/v1", params={
        "token": users[0]['token'], "dm_id": dm_1["dm_id"] + 1
    }).status_code == 400

    assert requests.get(url + "dm/details/v1", params={
        "token": users[0]['token'], "dm_id": dm_1["dm_id"] + 2
    }).status_code == 400

    assert requests.get(url + "dm/details/v1", params={
        "token": users[0]['token'], "dm_id": dm_1["dm_id"] + 3
    }).status_code == 400


def test_auth_not_member(users, dm_1):
    '''
    A test which checks if status code 403 is returned when the authorised user
    is not a member of the dm with dm_id
    '''
    new_user = requests.post(url + "auth/register/v2", json={
        "email": "new.email@gmail.com", "password": "abcdefgh", 
        "name_first": "N", "name_last": "E"
    })
    new_user = new_user.json()

    assert requests.get(url + "dm/details/v1", params={
        "token": new_user['token'], "dm_id": dm_1["dm_id"]
    }).status_code == 403


def test_invalid_token(dm_1):
    '''
    A test which checks if status code 403 is returned when the token passed in
    is not a valid id
    '''
    assert requests.get(
        url + "dm/details/v1", params={"token": "invalid token", "dm_id": dm_1["dm_id"]}
    ).status_code == 403

    assert requests.get(
        url + "dm/details/v1", params={"token": 1, "dm_id": dm_1["dm_id"]}
    ).status_code == 403

    assert requests.get(
        url + "dm/details/v1", params={"token": [1, 2, 3], "dm_id": dm_1["dm_id"]}
    ).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
