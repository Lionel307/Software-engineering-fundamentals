import pytest
import requests
import json

from src.config import url

@pytest.fixture
def users():
    requests.delete(url + "clear/v1")

    global_owner = requests.post(url + "/auth/register/v2", json={
        "email": "eru.iluvatar@gmail.com", "password": "123abc!@", "name_first": "Eru", "name_last": "Iluvatar" 
    })
    global_owner = global_owner.json()

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

    return [u1, u2, u3, global_owner]

@pytest.fixture
def channels(users):

    dm_1 = requests.post(url + "dm/create/v1", json={
        "token": users[0]["token"], "u_ids": [users[1]["auth_user_id"]]}).json()
    
    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": "test", "is_public": True
    }).json()

    return [dm_1, channel_1]

def test_user_profile(users):
    profile = requests.get(url + "user/profile/v2", params={"token": users[0]["token"], "u_id": users[3]["auth_user_id"]}).json()["user"]

    assert profile["name_first"] == "Eru"
    assert profile["name_last"] == "Iluvatar"
    assert profile["email"] == "eru.iluvatar@gmail.com"
    assert profile["handle_str"] == "eruiluvatar"
    assert profile["u_id"] == users[3]["auth_user_id"]

def test_user_profile_no_exist(users):

    assert requests.get(url + "user/profile/v2", params={"token": users[0]["token"], "u_id": 42}).status_code == 400


def test_set_name_email_handle(users, channels):

    name_first = "Lelouch"
    name_last = "Lamperouge"
    email = "lelouch.lamperouge@Britannia.com"
    handle = "Zero"

    requests.put(url + "user/profile/setname/v2", json={
        "token": users[0]["token"], "name_first": name_first, "name_last": name_last})

    requests.put(url + "user/profile/setemail/v2", json={
        "token": users[0]["token"], "email": email})

    requests.put(url + "user/profile/sethandle/v1", json={
        "token": users[0]["token"], "handle_str": handle})
    
    profile = requests.get(url + "user/profile/v2", params={"token": users[0]["token"], "u_id": users[0]["auth_user_id"]}).json()["user"]

    assert profile["name_first"] == name_first
    assert profile["name_last"] == name_last
    assert profile["email"] == email
    assert profile["handle_str"] == handle

    channel_details = requests.get(url + "channel/details/v2", params={
        "token": users[0]['token'], "channel_id": channels[1]["channel_id"]
    }).json()

    assert channel_details["owner_members"][0]["email"] == email
    assert channel_details["owner_members"][0]["handle_str"] == handle
    assert channel_details["owner_members"][0]["name_first"] == name_first
    assert channel_details["owner_members"][0]["name_last"] == name_last

    assert channel_details["all_members"][0]["email"] == email
    assert channel_details["all_members"][0]["handle_str"] == handle
    assert channel_details["all_members"][0]["name_first"] == name_first
    assert channel_details["all_members"][0]["name_last"] == name_last


    dm_details = requests.get(url + "dm/details/v1", params={
        "token": users[0]['token'], "dm_id": channels[0]["dm_id"]
    }).json()

    assert dm_details["members"][0]["email"] == email
    assert dm_details["members"][0]["handle_str"] == handle
    assert dm_details["members"][0]["name_first"] == name_first
    assert dm_details["members"][0]["name_last"] == name_last


def test_set_handle_already_in_use(users):
    handle = "harrypotter"

    assert requests.put(url + "user/profile/sethandle/v1", json={
        "token": users[0]["token"], "handle_str": handle}).status_code == 400

def test_set_handle_and_name_too_long_or_short(users):
    long_string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    name_first = "Lelouch"
    name_last = "Lamperouge"

    assert requests.put(url + "user/profile/sethandle/v1", json={
        "token": users[0]["token"], "handle_str": long_string}).status_code == 400

    assert requests.put(url + "user/profile/sethandle/v1", json={
        "token": users[0]["token"], "handle_str": "hi"}).status_code == 400

    assert requests.put(url + "user/profile/setname/v2", json={
        "token": users[0]["token"], "name_first": long_string, "name_last": name_last}).status_code == 400
    assert requests.put(url + "user/profile/setname/v2", json={
        "token": users[0]["token"], "name_first": name_first, "name_last": long_string}).status_code == 400

    assert requests.put(url + "user/profile/setname/v2", json={
        "token": users[0]["token"], "name_first": "", "name_last": name_last}).status_code == 400

    assert requests.put(url + "user/profile/setname/v2", json={
        "token": users[0]["token"], "name_first": name_first, "name_last": ""}).status_code == 400

def test_set_email_exceptions(users):
    invalid_email = "wrong$$$Email@gmail.com"
    used_email = "eru.iluvatar@gmail.com"

    assert requests.put(url + "user/profile/setemail/v2", json={
        "token": users[0]["token"], "email": used_email}).status_code == 400

    assert requests.put(url + "user/profile/setemail/v2", json={
        "token": users[0]["token"], "email": invalid_email}).status_code == 400

    requests.delete(url + "clear/v1")
