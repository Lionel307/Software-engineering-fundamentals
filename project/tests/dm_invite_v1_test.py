import pytest

from src.auth import auth_register_v2
from src.dm import dm_create_v1, dm_list_v1, dm_invite_v1, dm_details_v1
from src.other import clear_v1
from src.error import InputError, AccessError

@pytest.fixture
def users():
    clear_v1()
    user = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    user_2 = auth_register_v2('anothervalidemail@gmail.com', '123abc!@#', 'Hayden', 'Smith')
    user_3 = auth_register_v2('yetanothervalidemail@gmail.com', '123abc!@#', 'Nothayden', 'Smith')
    return [user, user_2, user_3]


def test_one_user_invited(users):
    new_dm = dm_create_v1(users[0]["token"], [])

    dm_invite_v1(users[0]["token"], new_dm["dm_id"], users[1]["auth_user_id"])

    list_of_dms = dm_list_v1(users[1]["token"])["dms"]

    assert list_of_dms[0]["dm_id"] == new_dm["dm_id"]
    assert list_of_dms[0]["name"] == new_dm["dm_name"]


def test_two_users_invited(users):
    new_dm = dm_create_v1(users[0]["token"], [])

    dm_invite_v1(users[0]["token"], new_dm["dm_id"], users[1]["auth_user_id"])
    dm_invite_v1(users[1]["token"], new_dm["dm_id"], users[2]["auth_user_id"])

    list_of_dms = dm_list_v1(users[2]["token"])["dms"]

    assert list_of_dms[0]["dm_id"] == new_dm["dm_id"]
    assert list_of_dms[0]["name"] == new_dm["dm_name"]

def test_invalid_dm_id(users):
    with pytest.raises(InputError):
        dm_invite_v1(users[0]["token"], 1, users[1]["auth_user_id"])
    
    with pytest.raises(InputError):
        dm_invite_v1(users[0]["token"], "hello", users[1]["auth_user_id"])

    with pytest.raises(InputError):
        dm_invite_v1(users[0]["token"], [1,2], users[1]["auth_user_id"])

def test_invalid_u_id(users):
    clear_v1()
    user = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    new_dm = dm_create_v1(user["token"], [])

    with pytest.raises(InputError):
        dm_invite_v1(user["token"], new_dm["dm_id"], users[1]["auth_user_id"])

    with pytest.raises(InputError):
        dm_invite_v1(user["token"], new_dm["dm_id"], users[2]["auth_user_id"])

    with pytest.raises(InputError):
        dm_invite_v1(user["token"], new_dm["dm_id"], "hello")

def test_not_a_member(users):

    new_dm = dm_create_v1(users[0]["token"], [])

    with pytest.raises(AccessError):
        dm_invite_v1(users[1]["token"], new_dm["dm_id"], users[2]["auth_user_id"])

    with pytest.raises(AccessError):
        dm_invite_v1(users[2]["token"], new_dm["dm_id"], users[0]["auth_user_id"])

def test_already_a_member(users):
    new_dm = dm_create_v1(users[0]["token"], [users[1]["auth_user_id"]])
    dm_invite_v1(users[0]["token"], new_dm["dm_id"], users[1]["auth_user_id"])

    dm_details = dm_details_v1(users[0]["token"], new_dm["dm_id"])
    counter = 0
    for member in dm_details["members"]:
        if member["u_id"] == users[1]["auth_user_id"]:
            counter = counter + 1
    assert counter == 1

    clear_v1()