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
def private_channel_id(users):
    '''
    Creates a private channel for use in tests
    '''
    private_channel = requests.post(url + "channels/create/v2", json={
        "token": users[2]['token'], "name": "private channel", "is_public": False
    })
    private_channel = private_channel.json()

    return private_channel["channel_id"]


def test_correct_return(users):
    '''
    A test which checks if the return value of the route is correct
    '''
    payload_1 = requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[0]['token'], "u_id": users[1]["auth_user_id"], 
        "permission_id": 1
    })
    payload_1 = payload_1.json()

    payload_2 = requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[0]['token'], "u_id": users[0]["auth_user_id"], 
        "permission_id": 2
    })
    payload_2 = payload_2.json()

    assert payload_1 == payload_2 and payload_2 == {}


def test_perms_changed(users, private_channel_id):
    '''
    A test which checks if the permissions of users are successfully changed
    by checking if they can or cannot join a private channel after having their 
    permissions changed 
    '''
    requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[0]['token'], "u_id": users[1]["auth_user_id"], 
        "permission_id": 1
    })

    requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[0]['token'], "u_id": users[2]["auth_user_id"], 
        "permission_id": 1
    })

    requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[1]['token'], "u_id": users[0]["auth_user_id"], 
        "permission_id": 2
    })

    join_result_1 = requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": private_channel_id
    })
    join_result_1 = join_result_1.json()

    join_result_2 = requests.post(url + "channel/join/v2", json={
        "token": users[2]['token'], "channel_id": private_channel_id
    })
    join_result_2 = join_result_2.json()

    # user 1 who is no longer a Dreams owner tries to join a private channel
    assert requests.post(url + "channel/join/v2", json={
        "token": users[0]['token'], "channel_id": private_channel_id
    }).status_code == 403

    # user 2 and 3 who are now Dreams owners try to join a private channel
    assert join_result_1 == join_result_2 and join_result_2 == {}


def test_invalid_u_id(users):
    '''
    A test which checks if status code 400 is returned when the u_id does not
    refer to a valid user
    '''
    requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[0]['token'], "u_id": users[2]['auth_user_id'] + 20000,
        "permission_id": 1
    }).status_code == 400
    
    requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[0]['token'], "u_id": [1, 2, 3],
        "permission_id": 1
    }).status_code == 400

    requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[0]['token'], "u_id": "invalid",
        "permission_id": 1
    }).status_code == 400


def test_wrong_permission_id(users):
    '''
    A test which checks if status code 400 is returned when permission_id does
    not refer to a valid permission
    '''
    requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[0]['token'], "u_id": users[1]['auth_user_id'],
        "permission_id": 0
    }).status_code == 400

    requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[0]['token'], "u_id": users[1]['auth_user_id'],
        "permission_id": -1
    }).status_code == 400

    requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[0]['token'], "u_id": users[1]['auth_user_id'],
        "permission_id": 3
    }).status_code == 400


def test_not_dreams_owner(users):
    '''
    A test which checks if status code 403 is returned when the authorised user is
    not an owner of Dreams
    '''
    requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[1]['token'], "u_id": users[2]['auth_user_id'],
        "permission_id": 1
    }).status_code == 403

    requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[1]['token'], "u_id": users[0]['auth_user_id'],
        "permission_id": 2
    }).status_code == 403


    requests.post(url + "admin/userpermission/change/v1", json={
        "token": users[2]['token'], "u_id": users[0]['auth_user_id'],
        "permission_id": 2
    }).status_code == 403


def test_invalid_token(users):
    '''
    A test which checks if status code 403 is returned when the token passed in
    is not a valid id
    '''
    # invalidates the token of user 1
    requests.post(url + "auth/logout/v1", json={"token": users[0]["token"]})

    assert requests.delete(url + "admin/user/remove/v1", json={
        "token": users[0]['token'], "u_id": users[1]['auth_user_id'],
        "permission_id": 1
    }).status_code == 403

    assert requests.delete(url + "admin/user/remove/v1", json={
        "token": "invalid", "u_id": users[1]['auth_user_id'],
        "permission_id": 1
    }).status_code == 403

    assert requests.delete(url + "admin/user/remove/v1", json={
        "token": 1, "u_id": users[1]['auth_user_id'],
        "permission_id": 1
    }).status_code == 403

    assert requests.delete(url + "admin/user/remove/v1", json={
        "token": [1, 2, 3], "u_id": users[1]['auth_user_id'],
        "permission_id": 1
    }).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
