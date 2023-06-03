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
def remove_user(users):
    '''
    Removes a user from Dreams for use in tests
    '''
    output = requests.delete(url + "admin/user/remove/v1", json={
        "token": users[0]['token'], "u_id": users[1]['auth_user_id']
    })

    return output.json()


def test_correct_return(remove_user):
    '''
    A test which checks if the return value of the route is correct
    '''
    assert remove_user == {}


def test_user_removed(users, remove_user):
    '''
    A test which checks if the user has been successfully removed from Dreams
    '''
    all_users = requests.get(url + "users/all/v1", params={"token": users[2]['token']})
    all_users = all_users.json()
    list_users = all_users['users']

    is_removed = True
    for user in list_users:
        if user['u_id'] == users[1]['auth_user_id']:
            is_removed = False

    assert is_removed == True


def test_user_profile(users, remove_user):
    '''
    A test which checks if the user profile is still retrievable with 
    user_profile_v2 (does not check the first name and last name
    is it is not well defined in the spec)
    '''
    resp = requests.get(url + "user/profile/v2", params={
        "token": users[2]['token'], "u_id": users[1]['auth_user_id']
    })
    resp = resp.json()
    r_user_profile = resp['user']

    assert r_user_profile['u_id'] == users[1]['auth_user_id']
    assert r_user_profile['email'] == 'anotheremail@gmail.com'
    assert r_user_profile['handle_str'] == 'ai'


def test_channel_messages_replaced(users):
    '''
    A test which checks if the user's messages in a channel have been replaced 
    by "Removed user"
    '''
    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": users[0]["token"], "name": "channel 1", "is_public": True
    })
    channel_1 = channel_1.json()
    channel_id_1 = channel_1['channel_id']

    requests.post(url + "channel/join/v2", json={
        "token": users[1]["token"], "channel_id": channel_id_1
    })

    requests.post(url + "message/send/v2", json={
        "token": users[1]["token"], "channel_id": channel_id_1, 
        "message": 'Hi'
    })

    requests.post(url + "message/send/v2", json={
        "token": users[1]["token"], "channel_id": channel_id_1, 
        "message": 'Hello'
    })

    requests.post(url + "message/send/v2", json={
        "token": users[1]["token"], "channel_id": channel_id_1, 
        "message": 'World'
    })

    requests.delete(url + "admin/user/remove/v1", json={
        "token": users[0]["token"], "u_id": users[1]['auth_user_id']
    })

    c_messages = requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": channel_id_1, "start": 0
    })
    c_messages = c_messages.json()
    list_messages = c_messages['messages']

    messages_removed = True
    for dict_message in list_messages:
        if not dict_message['message'] == 'Removed user':
            messages_removed = False

    assert messages_removed == True


def test_dm_messages_replaced(users):
    '''
    A test which checks if the user's messages in a dm have been replaced 
    by "Removed user"
    '''
    dm_1 = requests.post(url + "dm/create/v1", json={
        "token": users[0]["token"], "u_ids": [users[1]["auth_user_id"]]})
    dm_1 = dm_1.json()
    dm_id_1 = dm_1["dm_id"]

    requests.post(url + "message/senddm/v1", json={
        "token": users[1]["token"], "dm_id": dm_id_1, 
        "message": "Hi"
    })

    requests.post(url + "message/senddm/v1", json={
        "token": users[1]["token"], "dm_id": dm_id_1, 
        "message": "Hello"
    })

    requests.post(url + "message/senddm/v1", json={
        "token": users[1]["token"], "dm_id": dm_id_1, 
        "message": "World"
    })

    requests.delete(url + "admin/user/remove/v1", json={
        "token": users[0]['token'], "u_id": users[1]['auth_user_id']
    })

    dm_messages = requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": dm_id_1, "start": 0
    })
    dm_messages = dm_messages.json()
    list_messages = dm_messages['messages']

    messages_removed = True
    for dict_message in list_messages:
        if not dict_message['message'] == 'Removed user':
            messages_removed = False

    assert messages_removed == True


def test_invalid_u_id(users):
    '''
    A test which checks if status code 400 is returned when the u_id does not
    refer to a valid user
    '''
    requests.delete(url + "admin/user/remove/v1", json={
        "token": users[0]['token'], "u_id": users[2]['auth_user_id'] + 20000
    }).status_code == 400
    
    requests.delete(url + "admin/user/remove/v1", json={
        "token": users[0]['token'], "u_id": [1, 2, 3]
    }).status_code == 400

    requests.delete(url + "admin/user/remove/v1", json={
        "token": users[0]['token'], "u_id": "invalid"
    }).status_code == 400


def test_only_owner(users):
    '''
    A test which checks if status code 400 is returned when the user is currently
    the only Dreams owner
    '''
    requests.delete(url + "admin/user/remove/v1", json={
        "token": users[0]['token'], "u_id": users[0]['auth_user_id']
    }).status_code == 403


def test_not_owner(users):
    '''
    A test which checks if status code 403 is returned when the authorised user 
    is not a Dreams owner
    '''
    requests.delete(url + "admin/user/remove/v1", json={
        "token": users[1]['token'], "u_id": users[0]['auth_user_id']
    }).status_code == 403

    requests.delete(url + "admin/user/remove/v1", json={
        "token": users[2]['token'], "u_id": users[0]['auth_user_id']
    }).status_code == 403


def test_invalid_token(users):
    '''
    A test which checks if status code 403 is returned when the token passed in
    is not a valid id
    '''
    # invalidates the token of user 1
    requests.post(url + "auth/logout/v1", json={"token": users[0]["token"]})

    assert requests.delete(url + "admin/user/remove/v1", json={
        "token": users[0]['token'], "u_id": users[1]['auth_user_id']
    }).status_code == 403

    assert requests.delete(url + "admin/user/remove/v1", json={
        "token": "invalid", "u_id": users[1]['auth_user_id']
    }).status_code == 403

    assert requests.delete(url + "admin/user/remove/v1", json={
        "token": 1, "u_id": users[1]['auth_user_id']
    }).status_code == 403

    assert requests.delete(url + "admin/user/remove/v1", json={
        "token": [1, 2, 3], "u_id": users[1]['auth_user_id']
    }).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
