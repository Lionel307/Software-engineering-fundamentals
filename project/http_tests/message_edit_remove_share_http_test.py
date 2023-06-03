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
    dm_2 = requests.post(url + "dm/create/v1", json={
        "token": users[1]["token"], "u_ids": []}).json()
    
    channel_1 = requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": "test", "is_public": True
    }).json()

    channel_2 = requests.post(url + "channels/create/v2", json={
        "token": users[0]['token'], "name": "test_2", "is_public": True
    }).json()
    return [dm_1, dm_2, channel_1, channel_2]

def test_correct_message_removed_channel(users, channels):
    message_1 = "Hello World!"
    message_2 = "comp1531 is fun!!"

    for _ in range(20):
        requests.post(url + "message/send/v2", json={
            "token": users[0]["token"], "channel_id": channels[2]["channel_id"], "message": message_1
        })

    message_id = requests.post(url + "message/send/v2", json={
            "token": users[0]["token"], "channel_id": channels[2]["channel_id"], "message": message_2
        }).json()["message_id"]

    for _ in range(20):
        requests.post(url + "message/send/v2", json={
            "token": users[0]["token"], "channel_id": channels[2]["channel_id"], "message": message_1
        })

    
    requests.delete(url + "message/remove/v1", json={"token": users[0]["token"], "message_id": message_id})
    message_list = requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": channels[2]["channel_id"], "start": 0}).json()["messages"]


    is_removed = True
    for msg in message_list:
        if msg["message"] == message_2:
            is_removed = False
    assert is_removed == True

def test_correct_message_removed_dm(users, channels):
    message_1 = "Hello World!"
    message_2 = "comp1531 is fun!!"

    for _ in range(20):
        requests.post(url + "message/senddm/v1", json={
            "token": users[0]["token"], "dm_id": channels[0]["dm_id"], "message": message_1
        })

    message_id = requests.post(url + "message/senddm/v1", json={
            "token": users[0]["token"], "dm_id": channels[0]["dm_id"], "message": message_2
        }).json()["message_id"]

    for _ in range(20):
        requests.post(url + "message/senddm/v1", json={
            "token": users[0]["token"], "dm_id": channels[0]["dm_id"], "message": message_1
        })

    
    requests.delete(url + "message/remove/v1", json={"token": users[0]["token"], "message_id": message_id})
    message_list = requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": channels[0]["dm_id"], "start": 0}).json()["messages"]


    is_removed = True
    for msg in message_list:
        if msg["message"] == message_2:
            is_removed = False
    assert is_removed == True

def test_remove_unauthorised_user(users, channels):
    message = "Hello World!!"

    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channels[2]["channel_id"]
    })

    message_id_1 = requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channels[2]["channel_id"], "message": message
    }).json()["message_id"]

    message_id_2 = requests.post(url + "message/senddm/v1", json={
            "token": users[0]["token"], "dm_id": channels[0]["dm_id"], "message": message
        }).json()["message_id"]

    assert requests.delete(url + "message/remove/v1", json={"token": users[1]["token"], "message_id": message_id_1}).status_code == 403
    assert requests.delete(url + "message/remove/v1", json={"token": users[1]["token"], "message_id": message_id_2}).status_code == 403
    assert requests.delete(url + "message/remove/v1", json={"token": users[2]["token"], "message_id": message_id_2}).status_code == 403

def test_remove_owners(users, channels):
    message = "Hello World!!"

    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channels[2]["channel_id"]
    })

    message_id_1 = requests.post(url + "message/send/v2", json={
        "token": users[1]["token"], "channel_id": channels[2]["channel_id"], "message": message
    }).json()["message_id"]

    message_id_2 = requests.post(url + "message/senddm/v1", json={
            "token": users[1]["token"], "dm_id": channels[0]["dm_id"], "message": message
        }).json()["message_id"]

    assert requests.delete(url + "message/remove/v1", json={"token": users[0]["token"], "message_id": message_id_1}).status_code == 200
    assert requests.delete(url + "message/remove/v1", json={"token": users[3]["token"], "message_id": message_id_2}).status_code == 200

def test_remove_message_no_exist(users, channels):
    message = "Hello World!!"

    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channels[2]["channel_id"]
    })

    message_id_1 = requests.post(url + "message/send/v2", json={
        "token": users[1]["token"], "channel_id": channels[2]["channel_id"], "message": message
    }).json()["message_id"]

    message_id_2 = requests.post(url + "message/senddm/v1", json={
            "token": users[1]["token"], "dm_id": channels[0]["dm_id"], "message": message
        }).json()["message_id"]

    assert requests.delete(url + "message/remove/v1", json={"token": users[1]["token"], "message_id": message_id_1}).status_code == 200
    assert requests.delete(url + "message/remove/v1", json={"token": users[1]["token"], "message_id": message_id_1}).status_code == 400
    assert requests.delete(url + "message/remove/v1", json={"token": users[1]["token"], "message_id": message_id_2}).status_code == 200
    assert requests.delete(url + "message/remove/v1", json={"token": users[1]["token"], "message_id": message_id_2}).status_code == 400
    assert requests.delete(url + "message/remove/v1", json={"token": users[1]["token"], "message_id": 42}).status_code == 400

def test_edit_remove_message(users, channels):
    message = "Hello World!!"

    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channels[2]["channel_id"]
    })

    message_id_1 = requests.post(url + "message/send/v2", json={
        "token": users[1]["token"], "channel_id": channels[2]["channel_id"], "message": message
    }).json()["message_id"]

    message_id_2 = requests.post(url + "message/senddm/v1", json={
            "token": users[1]["token"], "dm_id": channels[0]["dm_id"], "message": message
        }).json()["message_id"]
    
    requests.put(url + "message/edit/v2", json={"token": users[1]["token"], "message_id": message_id_1, "message": ""})
    assert requests.delete(url + "message/remove/v1", json={"token": users[1]["token"], "message_id": message_id_1}).status_code == 400

    requests.put(url + "message/edit/v2", json={"token": users[1]["token"], "message_id": message_id_2, "message": ""})
    assert requests.delete(url + "message/remove/v1", json={"token": users[1]["token"], "message_id": message_id_2}).status_code == 400

def test_correct_message_edited_channel(users, channels):
    message_1 = "Hello World!"
    message_2 = "comp1531 is fun!!"

    for _ in range(20):
        requests.post(url + "message/send/v2", json={
            "token": users[0]["token"], "channel_id": channels[2]["channel_id"], "message": message_1
        })

    message_id = requests.post(url + "message/send/v2", json={
            "token": users[0]["token"], "channel_id": channels[2]["channel_id"], "message": message_2
        }).json()["message_id"]

    for _ in range(20):
        requests.post(url + "message/send/v2", json={
            "token": users[0]["token"], "channel_id": channels[2]["channel_id"], "message": message_1
        })

    requests.put(url + "message/edit/v2", json={"token": users[0]["token"], "message_id": message_id, "message": message_1})

    message_list = requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": channels[2]["channel_id"], "start": 0}).json()["messages"]

    for msg in message_list:
        assert msg["message"] == message_1

def test_correct_message_edited_dm(users, channels):
    message_1 = "Hello World!"
    message_2 = "comp1531 is fun!!"

    for _ in range(20):
        requests.post(url + "message/senddm/v1", json={
            "token": users[0]["token"], "dm_id": channels[0]["dm_id"], "message": message_1
        })

    message_id = requests.post(url + "message/senddm/v1", json={
            "token": users[0]["token"], "dm_id": channels[0]["dm_id"], "message": message_2
        }).json()["message_id"]

    for _ in range(20):
        requests.post(url + "message/senddm/v1", json={
            "token": users[0]["token"], "dm_id": channels[0]["dm_id"], "message": message_1
        })
    
    requests.put(url + "message/edit/v2", json={"token": users[0]["token"], "message_id": message_id, "message": message_1})
    message_list = requests.get(url + "dm/messages/v1", params={
        "token": users[0]["token"], "dm_id": channels[0]["dm_id"], "start": 0}).json()["messages"]

    for msg in message_list:
        assert msg["message"] == message_1

def test_edit_owners(users, channels):
    message = "Hello World!!"

    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channels[2]["channel_id"]
    })

    message_id_1 = requests.post(url + "message/send/v2", json={
        "token": users[1]["token"], "channel_id": channels[2]["channel_id"], "message": message
    }).json()["message_id"]

    message_id_2 = requests.post(url + "message/senddm/v1", json={
            "token": users[1]["token"], "dm_id": channels[0]["dm_id"], "message": message
        }).json()["message_id"]
    
    requests.put(url + "message/edit/v2", json={"token": users[3]["token"], "message_id": message_id_1, "message": ""})
    assert requests.delete(url + "message/remove/v1", json={"token": users[1]["token"], "message_id": message_id_1}).status_code == 400

    requests.put(url + "message/edit/v2", json={"token": users[0]["token"], "message_id": message_id_2, "message": ""})
    assert requests.delete(url + "message/remove/v1", json={"token": users[1]["token"], "message_id": message_id_2}).status_code == 400

def test_edit_exceptions(users, channels):
    message = "Hello World!!"
    message_2 = "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat: it was a hobbit-hole, and that means comfort. It had a perfectly round door like a porthole, painted green, with a shiny yellow brass knob in the exact middle. The door opened on to a tube-shaped hall like a tunnel: a very comfortable tunnel without smoke, with panelled walls, and floors tiled and carpeted, provided with polished chairs, and lots and lots of pegs for hats and coats - the hobbit was fond of visitors. The tunnel wound on and on, going fairly but not quite straight into the side of the hill - The Hill, as all the people for many miles round called it - and many little round doors opened out of it, first on one side and then on another. No going upstairs for the hobbit: bedrooms, bathrooms, cellars, pantries (lots of these), wardrobes (he had whole rooms devoted to clothes), kitchens, dining-rooms, all were on the same floor, and indeed on the same passage. The best rooms were all on the left-hand side (going in), for these were the only ones to have windows, deep-set round windows looking over his garden and meadows beyond, sloping down to the river."

    # Message doesn't exist
    assert requests.put(url + "message/edit/v2", json={"token": users[3]["token"], "message_id": 42, "message": message}).status_code == 400

    # Unauthorised User
    message_id = requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channels[2]["channel_id"], "message": message
    }).json()["message_id"]
    assert requests.put(url + "message/edit/v2", json={"token": users[1]["token"], "message_id": message_id, "message": message}).status_code == 403

    # Long message
    assert requests.put(url + "message/edit/v2", json={"token": users[0]["token"], "message_id": message_id, "message": message_2}).status_code == 400

def test_share_with_new_message_channel(users, channels):
    message = "Hello"
    new_message = "This iss a message"

    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channels[2]["channel_id"]
    })

    requests.post(url + "channel/join/v2", json={
        "token": users[1]['token'], "channel_id": channels[3]["channel_id"]
    })

    message_id = requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channels[2]["channel_id"], "message": message
    }).json()["message_id"]

    shared_message_id = requests.post(url + "message/share/v1", json={
        "token": users[1]["token"], "og_message_id": message_id, "message": new_message, "channel_id": channels[3]["channel_id"], "dm_id": -1
    }).json()["shared_message_id"]

    message_list = requests.get(url + "channel/messages/v2", params={
        "token": users[0]["token"], "channel_id": channels[3]["channel_id"], "start": 0}).json()["messages"]

    assert message_list[0]["message_id"] == shared_message_id
    assert message_list[0]["u_id"] == users[1]["auth_user_id"]
    assert message_list[0]["message"].find(message) != -1
    assert message_list[0]["message"].find(new_message) != -1

def test_share_with_new_message_dm(users, channels):
    message = "Hello"
    new_message = "This iss a message"

    message_id = requests.post(url + "message/senddm/v1", json={
        "token": users[0]["token"], "dm_id": channels[0]["dm_id"], "message": message
    }).json()["message_id"]

    shared_message_id = requests.post(url + "message/share/v1", json={
        "token": users[1]["token"], "og_message_id": message_id, "message": new_message, "channel_id": -1, "dm_id": channels[1]["dm_id"]
    }).json()["shared_message_id"]

    message_list = requests.get(url + "dm/messages/v1", params={
        "token": users[1]["token"], "dm_id": channels[1]["dm_id"], "start": 0}).json()["messages"]

    assert message_list[0]["message_id"] == shared_message_id
    assert message_list[0]["u_id"] == users[1]["auth_user_id"]
    assert message_list[0]["message"].find(message) != -1
    assert message_list[0]["message"].find(new_message) != -1

def test_share_exceptions(users, channels):
    message = "Hello"

    # Unauthorised user

    message_id = requests.post(url + "message/send/v2", json={
        "token": users[0]["token"], "channel_id": channels[2]["channel_id"], "message": message
    }).json()["message_id"]

    message_id_2 = requests.post(url + "message/senddm/v1", json={
        "token": users[0]["token"], "dm_id": channels[0]["dm_id"], "message": message
    }).json()["message_id"]

    assert requests.post(url + "message/share/v1", json={
        "token": users[0]["token"], "og_message_id": message_id_2, "message": "", "channel_id": -1, "dm_id": channels[1]["dm_id"]
    }).status_code == 403

    assert requests.post(url + "message/share/v1", json={
        "token": users[1]["token"], "og_message_id": message_id, "message": "", "channel_id": channels[3]["channel_id"], "dm_id": -1
    }).status_code == 403

    # Message_doesn't exist

    assert requests.post(url + "message/share/v1", json={
        "token": users[0]["token"], "og_message_id": 42, "message": "", "channel_id": -1, "dm_id": channels[1]["dm_id"]
    }).status_code == 400

    assert requests.post(url + "message/share/v1", json={
        "token": users[1]["token"], "og_message_id": 42, "message": "", "channel_id": channels[3]["channel_id"], "dm_id": -1
    }).status_code == 400

    requests.delete(url + "clear/v1")
