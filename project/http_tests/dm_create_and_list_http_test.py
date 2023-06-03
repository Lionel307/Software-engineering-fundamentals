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
    
    list_users = [user_1, user_2]

    return list_users


def test_dm_create_and_list(users):

    dm_1 = requests.post(url + "dm/create/v1", json={
        "token": users[0]["token"], "u_ids": [users[1]["auth_user_id"]]}).json()
    dm_2 = requests.post(url + "dm/create/v1", json={
        "token": users[1]["token"], "u_ids": []}).json()

    dm_list_1 = requests.get(url + "dm/list/v1", params={"token": users[0]["token"]}).json()["dms"]
    dm_list_2 = requests.get(url + "dm/list/v1", params={"token": users[1]["token"]}).json()["dms"]

    assert dm_list_1[0]["dm_id"] == dm_1["dm_id"]
    assert dm_list_1[0]["name"] == dm_1["dm_name"]

    assert {"dm_id": dm_1["dm_id"], "name": dm_1["dm_name"]} in dm_list_2
    assert {"dm_id": dm_2["dm_id"], "name": dm_2["dm_name"]} in dm_list_2

def test_list_100_dms(users):

    list_of_created = []
    for _ in range(100):
        dm_2 = requests.post(url + "dm/create/v1", json={
        "token": users[1]["token"], "u_ids": []}).json()
        list_of_created.append(dm_2)

    dm_list = requests.get(url + "dm/list/v1", params={"token": users[1]["token"]}).json()["dms"]
    dm_list_2 = requests.get(url + "dm/list/v1", params={"token": users[0]["token"]}).json()["dms"]

    for dm in list_of_created:
        assert {"dm_id": dm["dm_id"], "name": dm["dm_name"]} in dm_list

    assert len(dm_list_2) == 0


def test_create_invalid_user(users):

    assert requests.post(url + "dm/create/v1", json={
        "token": users[0]["token"], "u_ids": [users[1]["auth_user_id"] + 1]}).status_code == 400

    requests.delete(url + "clear/v1")
