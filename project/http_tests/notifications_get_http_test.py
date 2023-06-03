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
        "email": "validemail@gmail.com", "password": "123abc!@", "name_first": "M", "name_last": "J" 
    })
    u1 = u1.json()

    u2 = requests.post(url + "/auth/register/v2", json={
        "email": "ANOTHERVALIDEMAIL@gmail.com", "password": "Hello456abc!@", "name_first": "Hayden", "name_last": "Smith" 
    })
    u2 = u2.json()

    u3 = requests.post(url + "/auth/register/v2", json={
        "email": "harry.potter@gmail.com", "password": "Harry456abc!@", "name_first": "Nothayden", "name_last": "Smith" 
    })
    u3 = u3.json()

    return [u1, u2, u3, global_owner]

@pytest.fixture
def channels(users):

    
    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": "user 1's channel", "is_public": True
    }).json()

    dm_1 = requests.post(url + "dm/create/v1", json={
        "token": users[0]["token"], "u_ids": [users[1]["auth_user_id"], users[2]["auth_user_id"]]}).json()

    return [channel_1["channel_id"], dm_1["dm_id"]]


def test_several_users_tagged_message_send_and_added(users, channels):
    requests.post(url + "channel/invite/v2", json={
        "token": users[0]["token"], "channel_id": channels[0], 
        "u_id": users[1]["auth_user_id"]
    })
    requests.post(url + "channel/invite/v2", json={
        "token": users[0]["token"], "channel_id": channels[0], 
        "u_id": users[2]["auth_user_id"]
    })

    message = "Welcome to my channel @haydensmith and @nothaydensmith"

    requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channels[0], "message": message
    })

    cut_message = message[:20]

    notifications_1 = requests.get(url + "notifications/get/v1", params={"token": users[1]["token"]}).json()["notifications"]
    notifications_2 = requests.get(url + "notifications/get/v1", params={"token": users[2]["token"]}).json()["notifications"]

    notification_message = f"mj tagged you in user 1's channel: {cut_message}"

    assert notifications_1[0]["notification_message"] == notification_message
    assert notifications_1[0]["channel_id"] == channels[0]
    assert notifications_1[0]["dm_id"] == -1

    assert notifications_1[1]["notification_message"] == "mj added you to user 1's channel"
    assert notifications_1[1]["channel_id"] == channels[0]
    assert notifications_1[1]["dm_id"] == -1


    assert notifications_2[0]["notification_message"] == notification_message
    assert notifications_2[0]["channel_id"] == channels[0]
    assert notifications_2[0]["dm_id"] == -1
    

    assert notifications_2[1]["notification_message"] == "mj added you to user 1's channel"
    assert notifications_2[1]["channel_id"] == channels[0]
    assert notifications_2[1]["dm_id"] == -1

def test_several_users_tagged_dm_message(users, channels):
    message = "Welcome to my dm @haydensmith and @nothaydensmith"

    requests.post(url + "message/senddm/v1", json={
        "token": users[0]["token"], "dm_id": channels[1], "message": message
    })

    cut_message = message[:20]

    notifications_1 = requests.get(url + "notifications/get/v1", params={"token": users[1]["token"]}).json()["notifications"]
    notifications_2 = requests.get(url + "notifications/get/v1", params={"token": users[2]["token"]}).json()["notifications"]
    notification_message = f"mj tagged you in haydensmith, mj, nothaydensmith: {cut_message}"

    assert notifications_1[0]["notification_message"] == notification_message
    assert notifications_1[0]["channel_id"] == -1
    assert notifications_1[0]["dm_id"] == channels[1]

    assert notifications_1[1]["notification_message"] == "mj added you to haydensmith, mj, nothaydensmith"
    assert notifications_1[1]["channel_id"] == -1
    assert notifications_1[1]["dm_id"] == channels[1]

    assert notifications_2[0]["notification_message"] == notification_message
    assert notifications_2[0]["channel_id"] == -1
    assert notifications_2[0]["dm_id"] == channels[1]

    assert notifications_2[1]["notification_message"] == "mj added you to haydensmith, mj, nothaydensmith"
    assert notifications_2[1]["channel_id"] == -1
    assert notifications_2[1]["dm_id"] == channels[1]

def test_user_not_a_member():
    requests.delete(url + "clear/v1")
    message = "Welcome to my channel @haydensmith and @nothaydensmith"
    u1 = requests.post(url + "/auth/register/v2", json={
        "email": "validemail@gmail.com", "password": "123abc!@", "name_first": "M", "name_last": "J" 
    })
    u1 = u1.json()

    u2 = requests.post(url + "/auth/register/v2", json={
        "email": "ANOTHERVALIDEMAIL@gmail.com", "password": "Hello456abc!@", "name_first": "Hayden", "name_last": "Smith" 
    })
    u2 = u2.json()

    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": u1['token'], "name": "user 1's channel", "is_public": True
    }).json()

    requests.post(url + "message/send/v2", json={
        "token": u1["token"], "channel_id": channel_1["channel_id"], "message": message
    })

    notifications_1 = requests.get(url + "notifications/get/v1", params={"token": u2["token"]}).json()["notifications"]

    assert len(notifications_1) == 0


    requests.delete(url + "clear/v1")
