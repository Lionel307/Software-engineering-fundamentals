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

def test_several_users_reacting_and_unreacting_and_notif(users, channels):
    message = "hello"

    message_id = requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channels[0], "message": message
    }).json()["message_id"]

    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channels[0]
    })
    requests.post(url + "channel/join/v2", json={
        "token": users[2]['token'], "channel_id": channels[0]
    })

    requests.post(url + "message/react/v1", json={"token": users[0]["token"], "message_id": message_id, "react_id": 1})
    requests.post(url + "message/react/v1", json={"token": users[1]["token"], "message_id": message_id, "react_id": 1})

    message_list = requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": channels[0], "start": 0}).json()["messages"]

    assert users[0]["auth_user_id"] in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["react_id"] == 1
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == True

    message_list = requests.get(url + "channel/messages/v2", params={
        "token": users[1]["token"], "channel_id": channels[0], "start": 0}).json()["messages"]

    assert users[1]["auth_user_id"] in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == True

    message_list = requests.get(url + "channel/messages/v2", params={
        "token": users[2]["token"], "channel_id": channels[0], "start": 0}).json()["messages"]

    assert users[2]["auth_user_id"] not in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == False

    notifications = requests.get(url + "notifications/get/v1", params={"token": users[0]["token"]}).json()["notifications"]

    assert notifications[0]["channel_id"] == channels[0]
    assert notifications[0]["dm_id"] == -1
    assert notifications[0]["notification_message"] == "haydensmith reacted to your message in user 1's channel"

    requests.post(url + "message/unreact/v1", json={"token": users[1]["token"], "message_id": message_id, "react_id": 1})

    message_list = requests.get(url + "channel/messages/v2", params={
        "token": users[1]["token"], "channel_id": channels[0], "start": 0}).json()["messages"]
    
    assert users[1]["auth_user_id"] not in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == False

def test_in_dm(users, channels):
    message = "hello"

    message_id = requests.post(url + "message/senddm/v1", json={
        "token": users[0]["token"], "dm_id": channels[1], "message": message
    }).json()["message_id"]

    requests.post(url + "message/react/v1", json={"token": users[0]["token"], "message_id": message_id, "react_id": 1})

    message_list = requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": channels[1], "start": 0}).json()["messages"]
    
    assert message_list[0]["message_id"] == message_id
    assert users[0]["auth_user_id"] in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["react_id"] == 1
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == True

    requests.post(url + "message/unreact/v1", json={"token": users[0]["token"], "message_id": message_id, "react_id": 1})

    message_list = requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": channels[1], "start": 0}).json()["messages"]

    assert message_list[0]["message_id"] == message_id
    assert users[0]["auth_user_id"] not in message_list[0]["reacts"][0]["u_ids"]
    assert message_list[0]["reacts"][0]["react_id"] == 1
    assert message_list[0]["reacts"][0]["is_this_user_reacted"] == False

def test_exceptions(users, channels):
    # Invalid message id
    assert requests.post(url + "message/react/v1", json={"token": users[0]["token"], "message_id": 42343253, "react_id": 1}).status_code == 400
    assert requests.post(url + "message/unreact/v1", json={"token": users[0]["token"], "message_id": 235423542, "react_id": 1}).status_code == 400

    # Invalid react ID
    message_id = requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channels[0], "message": "hi"
    }).json()["message_id"]
    assert requests.post(url + "message/react/v1", json={"token": users[0]["token"], "message_id": message_id, "react_id": 2}).status_code == 400
    assert requests.post(url + "message/unreact/v1", json={"token": users[0]["token"], "message_id": message_id, "react_id": 2}).status_code == 400
    
    # Not a member
    assert requests.post(url + "message/react/v1", json={"token": users[1]["token"], "message_id": message_id, "react_id": 1}).status_code == 403
    assert requests.post(url + "message/unreact/v1", json={"token": users[1]["token"], "message_id": message_id, "react_id": 1}).status_code == 403

    # Already reacted or unreacted
    assert requests.post(url + "message/unreact/v1", json={"token": users[0]["token"], "message_id": message_id, "react_id": 1}).status_code == 400
    assert requests.post(url + "message/react/v1", json={"token": users[0]["token"], "message_id": message_id, "react_id": 1}).status_code == 200
    assert requests.post(url + "message/react/v1", json={"token": users[0]["token"], "message_id": message_id, "react_id": 1}).status_code == 400


    requests.delete(url + "clear/v1")
