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
        "name_first": "Hayden", "name_last": "Everest"
    })
    user_1 = user_1.json()

    user_2 = requests.post(url + "auth/register/v2", json={
        "email": "random@gmail.com", "password": "123abc!@#", 
        "name_first": "Random", "name_last": "Name"
    })
    user_2 = user_2.json()

    user_3 = requests.post(url + "auth/register/v2", json={
        "email": "dj@gmail.com", "password": "123abc!@#", 
        "name_first": "Doris", "name_last": "Johnson"
    })
    user_3 = user_3.json()

    list_users = [user_1, user_2, user_3]

    return list_users


def test_correct_output(users):
    '''
    A test which checks if the output of the route is correct
    '''
    expected_output = {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'validemail@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Everest',
                'handle_str': 'haydeneverest'
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'random@gmail.com',
                'name_first': 'Random',
                'name_last': 'Name',
                'handle_str': 'randomname'
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'dj@gmail.com',
                'name_first': 'Doris',
                'name_last': 'Johnson',
                'handle_str': 'dorisjohnson'
            }
        ]
    }
    
    resp = requests.get(url + "users/all/v1", params={"token": users[2]["token"]})
    payload = resp.json()

    assert payload == expected_output


def test_invalid_token():
    '''
    A test which checks if status code 403 is returned when an invalid 
    token is passed in
    '''
    assert requests.get(url + "users/all/v1", params={
        "token": "invalid token"
    }).status_code == 403

    assert requests.get(url + "users/all/v1", params={
        "token": 1
    }).status_code == 403

    assert requests.get(url + "channels/list/v2", params={
        "token": [1, 2, 3]
    }).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
