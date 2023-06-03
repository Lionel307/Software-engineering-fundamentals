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

@pytest.fixture
def dms(users):

    dm_1 = requests.post(url + "dm/create/v1", json={
        "token": users[0]["token"], "u_ids": [users[1]["auth_user_id"]]}).json()
    dm_2 = requests.post(url + "dm/create/v1", json={
        "token": users[1]["token"], "u_ids": []}).json()
    
    return [dm_1, dm_2]

def test_message_send(users, dms):
    message = "Programming in Python is fun @mj "

    message_id_1 = requests.post(url + "message/senddm/v1", json={
        "token": users[0]["token"], "dm_id": dms[0]["dm_id"], "message": message
    }).json()["message_id"]


    message_id_2 = requests.post(url + "message/senddm/v1", json={
        "token": users[1]["token"], "dm_id": dms[1]["dm_id"], "message": message
    }).json()["message_id"]


    message_list_1 = requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": dms[0]["dm_id"], "start": 0}).json()

    message_list_2 = requests.get(url + "dm/messages/v1", params={
        "token": users[1]["token"], "dm_id": dms[1]["dm_id"], "start": 0}).json()


    assert message_list_1["messages"][0]["message"] == message
    assert message_list_1["messages"][0]["message_id"] == message_id_1
    assert message_list_1["messages"][0]["u_id"] == users[0]["auth_user_id"]

    assert message_list_2["messages"][0]["message"] == message
    assert message_list_2["messages"][0]["message_id"] == message_id_2
    assert message_list_2["messages"][0]["u_id"] == users[1]["auth_user_id"]

def test_send_not_a_member(users, dms):
    message = "Programming in Python is fun"

    assert requests.post(url + "message/senddm/v1", json={
        "token": users[0]["token"], "dm_id": dms[1]["dm_id"], "message": message
    }).status_code == 403

def test_send_long_message(users, dms):
    message = "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat: it was a hobbit-hole, and that means comfort. It had a perfectly round door like a porthole, painted green, with a shiny yellow brass knob in the exact middle. The door opened on to a tube-shaped hall like a tunnel: a very comfortable tunnel without smoke, with panelled walls, and floors tiled and carpeted, provided with polished chairs, and lots and lots of pegs for hats and coats - the hobbit was fond of visitors. The tunnel wound on and on, going fairly but not quite straight into the side of the hill - The Hill, as all the people for many miles round called it - and many little round doors opened out of it, first on one side and then on another. No going upstairs for the hobbit: bedrooms, bathrooms, cellars, pantries (lots of these), wardrobes (he had whole rooms devoted to clothes), kitchens, dining-rooms, all were on the same floor, and indeed on the same passage. The best rooms were all on the left-hand side (going in), for these were the only ones to have windows, deep-set round windows looking over his garden and meadows beyond, sloping down to the river."

    assert requests.post(url + "message/senddm/v1", json={
        "token": users[0]["token"], "dm_id": dms[0]["dm_id"], "message": message
    }).status_code == 400

def test_send_invalid_dm_id(users, dms):
    message = "Programming in Python is fun"

    assert requests.post(url + "message/senddm/v1", json={
        "token": users[0]["token"], "dm_id": 42, "message": message
    }).status_code == 400

def test_messages_110_works(users, dms):

    list_of_messages_sent = []

    for x in range(110):
        message = f"test{x}"
        requests.post(url + "message/senddm/v1", json={
            "token": users[0]["token"], "dm_id": dms[0]["dm_id"], "message": message
        })
        list_of_messages_sent.append(message)

    message_list = requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": dms[0]["dm_id"], "start": 50}).json()

    message_list_2 = requests.get(url + "dm/messages/v1", params={
        "token": users[1]["token"], "dm_id": dms[1]["dm_id"], "start": 0}).json()
    
    assert len(message_list_2["messages"]) == 0

    list_of_messages_sent.reverse()

    y = 0
    for x in range(50, 100):
        assert list_of_messages_sent[x] == message_list["messages"][y]["message"]
        y = y + 1

    assert message_list["start"] == 50
    assert message_list["end"] == 100

def test_messages_invalid_channel(users):

    assert requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": 42, "start": 0}).status_code == 400

def test_messages_not_a_member(users, dms):

    assert requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": dms[1]["dm_id"], "start": 0}).status_code == 403

    requests.delete(url + "clear/v1")