import pytest
import requests
import json

from src.config import url

@pytest.fixture
def users():
    requests.delete(url + "clear/v1")

    u1 = requests.post(url + "/auth/register/v2", json={
        "email": "validemail@gmail.com", "password": "123abc!@", "name_first": "Hayden", "name_last": "Everest" 
    })
    u1 = u1.json()

    u2 = requests.post(url + "/auth/register/v2", json={
        "email": "ANOTHERVALIDEMAIL@gmail.com", "password": "Hello456abc!@", "name_first": "Thomas", "name_last": "Bobson" 
    })
    u2 = u2.json()

    u3 = requests.post(url + "/auth/register/v2", json={
        "email": "harry.potter@gmail.com", "password": "Harry456abc!@", "name_first": "Harry", "name_last": "Potter" 
    })
    u3 = u3.json()

    return [u1, u2, u3]

"""
Tests for auth/register/v2
"""

def test_valid_register_and_login(users):
    u1 = requests.post(url + "/auth/login/v2", json ={
        "email": "validemail@gmail.com", "password": "123abc!@"
    })
    u1 = u1.json()
    u2 = requests.post(url + "/auth/login/v2", json ={
        "email": "ANOTHERVALIDEMAIL@gmail.com", "password": "Hello456abc!@"
    })
    u2 = u2.json()
    u3 = requests.post(url + "/auth/login/v2", json ={
        "email": "harry.potter@gmail.com", "password": "Harry456abc!@"
    })
    u3 = u3.json()

    assert u1["auth_user_id"] == users[0]["auth_user_id"]
    assert u2["auth_user_id"] == users[1]["auth_user_id"]
    assert u3["auth_user_id"] == users[2]["auth_user_id"]

def test_invalid_email():
    requests.delete(url + "clear/v1")
    assert requests.post(url + "/auth/register/v2", json={
        "email": "wrong$$$Email@gmail.com", "password": "123abc!@", "name_first": "Hayden", "name_last": "Everest" 
    }).status_code == 400
    assert requests.post(url + "/auth/register/v2", json={
        "email": "wrongEmail!!@gmail.com", "password": "Hello456abc!@", "name_first": "Thomas", "name_last": "Bobson" 
    }).status_code == 400
    assert requests.post(url + "/auth/register/v2", json={
        "email": "wrongEmail@@gmail.com", "password": "Harry456abc!@", "name_first": "Harry", "name_last": "Potter"
    }).status_code == 400

def test_repeated_email(users):

    assert requests.post(url + "/auth/register/v2", json={
        "email": "validemail@gmail.com", "password": "123abc!@", "name_first": "Hayden", "name_last": "Everest" 
    }).status_code == 400

    assert requests.post(url + "/auth/register/v2", json={
        "email": "ANOTHERVALIDEMAIL@gmail.com", "password": "Hello456abc!@", "name_first": "Thomas", "name_last": "Bobson" 
    }).status_code == 400

    assert requests.post(url + "/auth/register/v2", json={
        "email": "harry.potter@gmail.com", "password": "Harry456abc!@", "name_first": "Harry", "name_last": "Potter" 
    }).status_code == 400

def test_short_password():
    requests.delete(url + "clear/v1")

    assert requests.post(url + "/auth/register/v2", json={
        "email": "validemail@gmail.com", "password": "ab2#", "name_first": "Hayden", "name_last": "Everest" 
    }).status_code == 400

    assert requests.post(url + "/auth/register/v2", json={
        "email": "ANOTHERVALIDEMAIL@gmail.com", "password": "pass", "name_first": "Thomas", "name_last": "Bobson" 
    }).status_code == 400

    assert requests.post(url + "/auth/register/v2", json={
        "email": "harry.potter@gmail.com", "password": "1", "name_first": "Harry", "name_last": "Potter" 
    }).status_code == 400

def test_short_password_edge_cases():
    requests.delete(url + "clear/v1")

    assert requests.post(url + "/auth/register/v2", json={
        "email": "validemail@gmail.com", "password": "p!wr#", "name_first": "Hayden", "name_last": "Everest" 
    }).status_code == 400

    assert requests.post(url + "/auth/register/v2", json={
        "email": "ANOTHERVALIDEMAIL@gmail.com", "password": "", "name_first": "Thomas", "name_last": "Bobson" 
    }).status_code == 400

def test_invalid_name():
    requests.delete(url + "clear/v1")
    long_name = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    assert requests.post(url + "/auth/register/v2", json={
        "email": "validemail@gmail.com", "password": "123abc!@", "name_first": "", "name_last": "Everest" 
    }).status_code == 400

    assert requests.post(url + "/auth/register/v2", json={
        "email": "ANOTHERVALIDEMAIL@gmail.com", "password": "Hello456abc!@", "name_first": long_name, "name_last": "Bobson" 
    }).status_code == 400

    assert requests.post(url + "/auth/register/v2", json={
        "email": "harry.potter@gmail.com", "password": "Harry456abc!@", "name_first": "Harry", "name_last": long_name 
    }).status_code == 400

    assert requests.post(url + "/auth/register/v2", json={
        "email": "harry.potter@gmail.com", "password": "Harry456abc!@", "name_first": "Harry", "name_last": ""
    }).status_code == 400

def test_same_names():
    requests.delete(url + "clear/v1")

    u1 = requests.post(url + "/auth/register/v2", json={
        "email": "validemail@gmail.com", "password": "123abc!@", "name_first": "Haydenhayden", "name_last": "Smithsmith" 
    }).json()

    u2 = requests.post(url + "/auth/register/v2", json={
        "email": "ANOTHERVALIDEMAIL@gmail.com", "password": "Hello456abc!@", "name_first": "Haydenhayden", "name_last": "Smithsmith" 
    }).json()

    u3 = requests.post(url + "/auth/register/v2", json={
        "email": "harry.potter@gmail.com", "password": "Harry456abc!@", "name_first": "Haydenhayden", "name_last": "Smithsmith" 
    }).json()
    test_valid_register_and_login([u1, u2, u3])

"""
Tests for auth/login/v2
"""

def test_login_invalid_emails():
    assert requests.post(url + "/auth/login/v2", json ={
        "email": "wrong$$$Email@gmail.com", "password": "123abc!@"
    }).status_code == 400
    assert requests.post(url + "/auth/login/v2", json ={
        "email": "wrongEmail!!@gmail.com", "password": "123abc!@"
    }).status_code == 400
    assert requests.post(url + "/auth/login/v2", json ={
        "email": "wrongEmail@@gmail.com", "password": "123abc!@"
    }).status_code == 400


def test_unregistered_emails():
    requests.delete(url + "clear/v1")

    u1 = requests.post(url + "/auth/login/v2", json ={
        "email": "validemail@gmail.com", "password": "123abc!@"
    })
    assert u1.status_code == 400
    u2 = requests.post(url + "/auth/login/v2", json ={
        "email": "ANOTHERVALIDEMAIL@gmail.com", "password": "Hello456abc!@"
    })
    assert u2.status_code == 400
    u3 = requests.post(url + "/auth/login/v2", json ={
        "email": "harry.potter@gmail.com", "password": "Harry456abc!@"
    })
    assert u3.status_code == 400

def test_wrong_password(users):
    u1 = requests.post(url + "/auth/login/v2", json ={
        "email": "validemail@gmail.com", "password": "123abc"
    })
    assert u1.status_code == 400
    u2 = requests.post(url + "/auth/login/v2", json ={
        "email": "ANOTHERVALIDEMAIL@gmail.com", "password": "Hello"
    })
    assert u2.status_code == 400
    u3 = requests.post(url + "/auth/login/v2", json ={
        "email": "harry.potter@gmail.com", "password": "wrongpassword"
    })
    assert u3.status_code == 400

def test_token_works(users):
    u1 = requests.post(url + "/auth/login/v2", json ={
        "email": "validemail@gmail.com", "password": "123abc!@"
    })
    u1 = u1.json()
    u2 = requests.post(url + "/auth/login/v2", json ={
        "email": "ANOTHERVALIDEMAIL@gmail.com", "password": "Hello456abc!@"
    })
    u2 = u2.json()
    u3 = requests.post(url + "/auth/login/v2", json ={
        "email": "harry.potter@gmail.com", "password": "Harry456abc!@"
    })
    u3 = u3.json()

    assert requests.get(url + "channels/listall/v2", params={"token": u1['token']}).status_code == 200
    assert requests.get(url + "channels/listall/v2", params={"token": u2['token']}).status_code == 200
    assert requests.get(url + "channels/listall/v2", params={"token": u3['token']}).status_code == 200

"""
Tests for auth/logout/v1
"""

def test_logout_returns_success(users):
    user = []
    user.append(requests.post(url + "/auth/logout/v1", json={"token": users[0]["token"]}).json())
    user.append(requests.post(url + "/auth/logout/v1", json={"token": users[1]["token"]}).json())
    user.append(requests.post(url + "/auth/logout/v1", json={"token": users[2]["token"]}).json())
    for u in user:
        assert u["is_success"] == True

def test_logout_invalidates_token(users):

    requests.post(url + "/auth/logout/v1", json={"token": users[0]["token"]})
    requests.post(url + "/auth/logout/v1", json={"token": users[1]["token"]})
    requests.post(url + "/auth/logout/v1", json={"token": users[2]["token"]})

    assert requests.get(url + "channels/listall/v2", params={"token": users[0]['token']}).status_code == 403
    assert requests.get(url + "channels/listall/v2", params={"token": users[1]['token']}).status_code == 403
    assert requests.get(url + "channels/listall/v2", params={"token": users[2]['token']}).status_code == 403

def test_logout_twice(users):

    requests.post(url + "/auth/logout/v1", json={"token": users[0]["token"]})
    requests.post(url + "/auth/logout/v1", json={"token": users[1]["token"]})
    requests.post(url + "/auth/logout/v1", json={"token": users[2]["token"]})

    assert requests.post(url + "/auth/logout/v1", json={"token": users[0]["token"]}).status_code == 403
    assert requests.post(url + "/auth/logout/v1", json={"token": users[1]["token"]}).status_code == 403
    assert requests.post(url + "/auth/logout/v1", json={"token": users[2]["token"]}).status_code == 403

def test_invalid_tokens():

    assert requests.post(url + "/auth/logout/v1", json={"token": 42}).status_code == 403
    assert requests.post(url + "/auth/logout/v1", json={"token": [1, 2, 3]}).status_code == 403
    assert requests.post(url + "/auth/logout/v1", json={"token": {"token": 1}}).status_code == 403

    requests.delete(url + "clear/v1")
