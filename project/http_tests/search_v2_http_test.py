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
def channel_ids(users):
    '''
    Creates channels and adds a user 3 to channel 1 for use in tests
    '''
    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": users[0]["token"], "name": "channel 1", "is_public": True
    })
    channel_1 = channel_1.json()
    
    channel_2 = requests.post(url + "channels/create/v2", json={
        "token": users[1]["token"], "name": "channel 1", "is_public": True
    })
    channel_2 = channel_2.json()
    
    requests.post(url + "channel/join/v2", json={
        "token": users[2]["token"], "channel_id": channel_1['channel_id']
    })

    list_channel_ids = [channel_1['channel_id'], channel_2['channel_id']]

    return list_channel_ids


@pytest.fixture
def dm_ids(users):
    '''
    Creates dms for use in tests
    '''
    dm_1 = requests.post(url + "dm/create/v1", json={
        "token": users[0]["token"], "u_ids": [users[1]["auth_user_id"]]})
    dm_1 = dm_1.json()
    dm_id_1 = dm_1["dm_id"]

    dm_2 = requests.post(url + "dm/create/v1", json={
        "token": users[2]["token"], "u_ids": [users[1]["auth_user_id"]]})
    dm_2 = dm_2.json()
    dm_id_2 = dm_2["dm_id"]

    list_dm_ids = [dm_id_1, dm_id_2]

    return list_dm_ids


@pytest.fixture
def c_message_ids(users, channel_ids):
    '''
    Sends messages in channels and returns the ones which have the word "message" 
    in them for use in tests
    '''
    matching_message_1 = requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channel_ids[0], 
        "message": 'New message'
    })
    matching_message_1 = matching_message_1.json()
    matching_message_id_1 = matching_message_1['message_id']

    matching_message_2 = requests.post(url + "message/send/v2", json={
        "token": users[2]["token"], "channel_id": channel_ids[0], 
        "message": 'another message'
    })
    matching_message_2 = matching_message_2.json()
    matching_message_id_2 = matching_message_2['message_id']

    requests.post(url + "message/send/v2", json={
        "token": users[1]["token"], "channel_id": channel_ids[1], 
        "message": 'new channel new message'
    })

    requests.post(url + "message/send/v2", json={
        "token": users[2]["token"], "channel_id": channel_ids[0], 
        "message": 'hi'
    })

    matching_message_ids = [matching_message_id_1, matching_message_id_2]

    return matching_message_ids


@pytest.fixture
def d_message_ids(users, dm_ids):
    '''
    Sends messages in dms and returns the ones which have the word "message" 
    in them for use in tests
    '''
    requests.post(url + "message/senddm/v1", json={
        "token": users[0]["token"], "dm_id": dm_ids[0], 
        "message": 'dm message'
    })

    requests.post(url + "message/senddm/v1", json={
        "token": users[1]["token"], "dm_id": dm_ids[1], 
        "message": 'hello'
    })

    matching_message_1 = requests.post(url + "message/senddm/v1", json={
        "token": users[2]["token"], "dm_id": dm_ids[1], 
        "message": 'random message'
    })
    matching_message_1 = matching_message_1.json()
    matching_message_id_1 = matching_message_1['message_id']

    matching_message_2 = requests.post(url + "message/senddm/v1", json={
        "token": users[1]["token"], "dm_id": dm_ids[1], 
        "message": 'new dm new message'
    })
    matching_message_2 = matching_message_2.json()
    matching_message_id_2 = matching_message_2['message_id']

    matching_message_ids = [matching_message_id_1, matching_message_id_2]

    return matching_message_ids


def test_no_matches(users, c_message_ids, d_message_ids):
    '''
    A test which checks the output of the route when no messages match query_str  
    '''
    output = requests.get(url + "search/v2", params={
        "token": users[2]["token"], "query_str": "query"
    })
    output = output.json()

    assert output == {"messages": []}


def test_matches(users, c_message_ids, d_message_ids):
    '''
    A test which checks the output of the function when multiple messages match query_str
    '''

    output = requests.get(url + "search/v2", params={
        "token": users[2]["token"], "query_str": "message"
    })
    output = output.json()
    output_messages = output["messages"]

    matches = c_message_ids
    matches.extend(d_message_ids)

    matches_correct = True
    num_matches = 0
    for message in output_messages:
        if not message['message_id'] in matches:
            matches_correct = False

        if message['message_id'] in matches:
            num_matches += 1

    assert num_matches == len(matches)
    assert matches_correct == True


def test_invalid_query_str(users):
    '''
    A test which checks if status code 400 is returned when query_str is above 1000 characters
    '''
    long_string = (
        "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, "
        "with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing "
        "in it to sit down on or to eat: it was a hobbit-hole, and that means comfort. It had a "
        "perfectly round door like a porthole, painted green, with a shiny yellow brass knob in " 
        "the exact middle. The door opened on to a tube-shaped hall like a tunnel: a very "
        "comfortable tunnel without smoke, with panelled walls, and floors tiled and carpeted, "
        "provided with polished chairs, and lots and lots of pegs for hats and coats - the "
        "hobbit was fond of visitors. The tunnel wound on and on, going fairly but not quite "
        "straight into the side of the hill - The Hill, as all the people for many miles round "
        "called it - and many little round doors opened out of it, first on one side and then "
        "on another. No going upstairs for the hobbit: bedrooms, bathrooms, cellars, "
        "pantries (lots of these), wardrobes (he had whole rooms devoted to clothes), kitchens, "
        "dining-rooms, all were on the same floor, and indeed on the same passage. The best rooms "
        "were all on the left-hand side (going in), for these were the only ones to have windows, "
        "deep-set round windows looking over his garden and meadows beyond, sloping down to the "
        "river."
    )

    assert requests.get(url + "search/v2", params={
        "token": users[0]["token"], "query_str": long_string
    }).status_code == 400
    
    assert requests.get(url + "search/v2", params={
        "token": users[1]["token"], "query_str": long_string
    }).status_code == 400

    assert requests.get(url + "search/v2", params={
        "token": users[2]["token"], "query_str": long_string
    }).status_code == 400


def test_invalid_token(users):
    '''
    A test which checks if status code 403 is returned when the token passed in
    is not a valid id
    '''
    # invalidates the token of user 1
    requests.post(url + "auth/logout/v1", json={"token": users[0]["token"]})

    assert requests.get(
        url + "search/v2", params={"token": users[0]["token"], "query_str": "query"
    }).status_code == 403

    assert requests.get(
        url + "search/v2", params={"token": "invalid token", "query_str": "query"
    }).status_code == 403

    assert requests.get(
        url + "search/v2", params={"token": 1, "query_str": "query"
    }).status_code == 403

    assert requests.get(
        url + "search/v2", params={"token": [1, 2, 3], "query_str": "query"
    }).status_code == 403

    # To clear the persistent data file once all the tests have been executed
    requests.delete(url + "clear/v1")
