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

    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": "test", "is_public": True
    }).json()["channel_id"]

    channel_2 = requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": "test2", "is_public": True
    }).json()["channel_id"]
    
    return [channel_1, channel_2]


def test_message_send(users, channels):
    message = "Programming in Python is fun @mj "

    message_id_1 = requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channels[0], "message": message
    }).json()["message_id"]

    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channels[1]
    })

    message_id_2 = requests.post(url + "message/send/v2", json={
        "token": users[1]["token"], "channel_id": channels[1], "message": message
    }).json()["message_id"]


    message_list_1 = requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": channels[0], "start": 0}).json()

    message_list_2 = requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": channels[1], "start": 0}).json()


    assert message_list_1["messages"][0]["message"] == message
    assert message_list_1["messages"][0]["message_id"] == message_id_1
    assert message_list_1["messages"][0]["u_id"] == users[0]["auth_user_id"]

    assert message_list_2["messages"][0]["message"] == message
    assert message_list_2["messages"][0]["message_id"] == message_id_2
    assert message_list_2["messages"][0]["u_id"] == users[1]["auth_user_id"]

def test_send_not_a_member(users, channels):
    message = "Programming in Python is fun"

    assert requests.post(url + "message/send/v2", json={
        "token": users[1]["token"], "channel_id": channels[0], "message": message
    }).status_code == 403

    assert requests.post(url + "message/send/v2", json={
        "token": users[2]["token"], "channel_id": channels[0], "message": message
    }).status_code == 403


    assert requests.post(url + "message/send/v2", json={
        "token": users[3]["token"], "channel_id": channels[0], "message": message
    }).status_code == 403

def test_send_long_message(users, channels):
    message = "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat: it was a hobbit-hole, and that means comfort. It had a perfectly round door like a porthole, painted green, with a shiny yellow brass knob in the exact middle. The door opened on to a tube-shaped hall like a tunnel: a very comfortable tunnel without smoke, with panelled walls, and floors tiled and carpeted, provided with polished chairs, and lots and lots of pegs for hats and coats - the hobbit was fond of visitors. The tunnel wound on and on, going fairly but not quite straight into the side of the hill - The Hill, as all the people for many miles round called it - and many little round doors opened out of it, first on one side and then on another. No going upstairs for the hobbit: bedrooms, bathrooms, cellars, pantries (lots of these), wardrobes (he had whole rooms devoted to clothes), kitchens, dining-rooms, all were on the same floor, and indeed on the same passage. The best rooms were all on the left-hand side (going in), for these were the only ones to have windows, deep-set round windows looking over his garden and meadows beyond, sloping down to the river."

    assert requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channels[0], "message": message
    }).status_code == 400

def test_send_invalid_channel(users):
    message = "Programming in Python is fun"

    assert requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": 42, "message": message
    }).status_code == 400

def test_110_messages_works(users, channels):

    list_of_messages_sent = []
    list_of_message_ids = []
    for x in range(110):
        message = f"test{x}"
        message_id = requests.post(url + "message/send/v2", json={
            "token": users[0]["token"], "channel_id": channels[0], "message": message
        }).json()["message_id"]
        list_of_messages_sent.append(message)
        list_of_message_ids.append(message_id)


    message_list = requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": channels[0], "start": 50}).json()

    list_of_messages_sent.reverse()
    list_of_message_ids.reverse()

    y = 0
    for x in range(50, 100):
        assert list_of_messages_sent[x] == message_list["messages"][y]["message"]
        assert list_of_message_ids[x] == message_list["messages"][y]["message_id"]

        y = y + 1
    
    assert message_list["start"] == 50
    assert message_list["end"] == 100

def test_messages_invalid_channel(users):
    assert requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": 42, "start": 0}).status_code == 400

def test_messages_user_not_a_member(users, channels):
    assert requests.get(url + "channel/messages/v2", params={
        "token": users[1]["token"], "channel_id": channels[0], "start": 0}).status_code == 403

    requests.delete(url + "clear/v1")
