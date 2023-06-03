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

    return [u1, u2, global_owner]

@pytest.fixture
def channels(users):
    
    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": "user 1's channel", "is_public": True
    }).json()

    dm_1 = requests.post(url + "dm/create/v1", json={
        "token": users[0]["token"], "u_ids": [users[1]["auth_user_id"]]}).json()

    return [channel_1["channel_id"], dm_1["dm_id"]]

def test_pining_and_unpining_several_messages(users, channels):
    message_1 = "hello"
    message_2 = "bye"

    message_id_1 = requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channels[0], "message": message_1
    }).json()["message_id"]

    message_id_2 = requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channels[0], "message": message_2
    }).json()["message_id"]

    requests.post(url + "message/pin/v1", json={"token": users[0]["token"], "message_id": message_id_1})
    requests.post(url + "message/pin/v1", json={"token": users[0]["token"], "message_id": message_id_2})

    message_list = requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": channels[0], "start": 0}).json()["messages"]

    assert message_list[0]["is_pinned"] == True
    assert message_list[1]["is_pinned"] == True

    requests.post(url + "message/unpin/v1", json={"token": users[0]["token"], "message_id": message_id_1})
    requests.post(url + "message/unpin/v1", json={"token": users[0]["token"], "message_id": message_id_2})

    message_list = requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": channels[0], "start": 0}).json()["messages"]
    
    assert message_list[0]["is_pinned"] == False
    assert message_list[1]["is_pinned"] == False

def test_in_dm(users, channels):
    message = "hello"

    message_id = requests.post(url + "message/senddm/v1", json={
        "token": users[0]["token"], "dm_id": channels[1], "message": message
    }).json()["message_id"]

    requests.post(url + "message/pin/v1", json={"token": users[0]["token"], "message_id": message_id})

    message_list = requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": channels[1], "start": 0}).json()["messages"]
    
    assert message_list[0]["message_id"] == message_id
    assert message_list[0]["is_pinned"] == True

    requests.post(url + "message/unpin/v1", json={"token": users[0]["token"], "message_id": message_id})

    message_list = requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": channels[1], "start": 0}).json()["messages"]

    assert message_list[0]["message_id"] == message_id
    assert message_list[0]["is_pinned"] == False

def test_exceptions(users, channels):
    # Invalid message id
    assert requests.post(url + "message/pin/v1", json={"token": users[0]["token"], "message_id": 42343253}).status_code == 400
    assert requests.post(url + "message/unpin/v1", json={"token": users[0]["token"], "message_id": 235423542}).status_code == 400
    
    message_id = requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channels[0], "message": "hi"
    }).json()["message_id"]

    # Not a member
    assert requests.post(url + "message/pin/v1", json={"token": users[1]["token"], "message_id": message_id}).status_code == 403
    assert requests.post(url + "message/unpin/v1", json={"token": users[1]["token"], "message_id": message_id}).status_code == 403

    # Already pinned or unpinned
    assert requests.post(url + "message/unpin/v1", json={"token": users[0]["token"], "message_id": message_id}).status_code == 400
    assert requests.post(url + "message/pin/v1", json={"token": users[0]["token"], "message_id": message_id}).status_code == 200
    assert requests.post(url + "message/pin/v1", json={"token": users[0]["token"], "message_id": message_id}).status_code == 400

    # Not owner
    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channels[0]
    })
    assert requests.post(url + "message/pin/v1", json={"token": users[1]["token"], "message_id": message_id}).status_code == 403
    assert requests.post(url + "message/unpin/v1", json={"token": users[1]["token"], "message_id": message_id}).status_code == 403
    requests.delete(url + "clear/v1")
