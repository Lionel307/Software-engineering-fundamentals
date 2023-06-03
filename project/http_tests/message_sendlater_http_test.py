import pytest
import requests
import json
import datetime
import time

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

    dm_2 = requests.post(url + "dm/create/v1", json={
        "token": users[0]["token"], "u_ids": []}).json()["dm_id"]
    
    return [channel_1, dm_2]

def test_channel_and_dm_sendlater_one_message(users, channels):
    message = "Hello There"

    utc_time = datetime.datetime.now(datetime.timezone.utc)
    current_time = int(utc_time.replace(tzinfo=datetime.timezone.utc).timestamp())
    send_time = current_time + 1

    message_id = requests.post(url + "message/sendlater/v1", json={
        "token": users[0]["token"], "channel_id": channels[0], "message": message, "time_sent": send_time
    }).json()["message_id"]

    message_id_dm = requests.post(url + "message/sendlaterdm/v1", json={
        "token": users[0]["token"], "dm_id": channels[1], "message": message, "time_sent": send_time
    }).json()["message_id"]

    channel_messages_list = requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": channels[0], "start": 0}).json()["messages"]

    dm_messages_list = requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": channels[1], "start": 0}).json()["messages"]

    assert len(channel_messages_list) == 0
    assert len(dm_messages_list) == 0

    time.sleep(1.6)

    channel_messages_list = requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": channels[0], "start": 0}).json()["messages"]

    dm_messages_list = requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": channels[1], "start": 0}).json()["messages"]

    assert channel_messages_list[0]["message"] == message
    assert channel_messages_list[0]["message_id"] == message_id
    assert channel_messages_list[0]["time_created"] == send_time

    assert dm_messages_list[0]["message"] == message
    assert dm_messages_list[0]["message_id"] == message_id_dm
    assert dm_messages_list[0]["time_created"] == send_time

def test_exceptions(users, channels):
    message = "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat: it was a hobbit-hole, and that means comfort. It had a perfectly round door like a porthole, painted green, with a shiny yellow brass knob in the exact middle. The door opened on to a tube-shaped hall like a tunnel: a very comfortable tunnel without smoke, with panelled walls, and floors tiled and carpeted, provided with polished chairs, and lots and lots of pegs for hats and coats - the hobbit was fond of visitors. The tunnel wound on and on, going fairly but not quite straight into the side of the hill - The Hill, as all the people for many miles round called it - and many little round doors opened out of it, first on one side and then on another. No going upstairs for the hobbit: bedrooms, bathrooms, cellars, pantries (lots of these), wardrobes (he had whole rooms devoted to clothes), kitchens, dining-rooms, all were on the same floor, and indeed on the same passage. The best rooms were all on the left-hand side (going in), for these were the only ones to have windows, deep-set round windows looking over his garden and meadows beyond, sloping down to the river."

    utc_time = datetime.datetime.now(datetime.timezone.utc)
    current_time = int(utc_time.replace(tzinfo=datetime.timezone.utc).timestamp())
    send_time = current_time + 100

    assert requests.post(url + "message/sendlater/v1", json={
        "token": users[0]["token"], "channel_id": channels[0], "message": message, "time_sent": send_time
    }).status_code == 400

    assert requests.post(url + "message/sendlaterdm/v1", json={
        "token": users[0]["token"], "dm_id": channels[1], "message": message, "time_sent": send_time
    }).status_code == 400

    message = "Hello There"

    assert requests.post(url + "message/sendlater/v1", json={
        "token": users[1]["token"], "channel_id": channels[0], "message": message, "time_sent": send_time
    }).status_code == 403

    assert requests.post(url + "message/sendlaterdm/v1", json={
        "token": users[1]["token"], "dm_id": channels[1], "message": message, "time_sent": send_time
    }).status_code == 403

    assert requests.post(url + "message/sendlater/v1", json={
        "token": users[0]["token"], "channel_id": 42, "message": message, "time_sent": send_time
    }).status_code == 400

    assert requests.post(url + "message/sendlaterdm/v1", json={
        "token": users[0]["token"], "dm_id": 42, "message": message, "time_sent": send_time
    }).status_code == 400

    send_time = send_time - 200

    assert requests.post(url + "message/sendlater/v1", json={
        "token": users[0]["token"], "channel_id": channels[0], "message": message, "time_sent": send_time
    }).status_code == 400

    assert requests.post(url + "message/sendlaterdm/v1", json={
        "token": users[0]["token"], "dm_id": channels[1], "message": message, "time_sent": send_time
    }).status_code == 400

    requests.delete(url + "clear/v1")
