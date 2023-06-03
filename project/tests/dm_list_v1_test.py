import pytest

from src.auth import auth_register_v2
from src.dm import dm_create_v1, dm_list_v1
from src.other import clear_v1


@pytest.fixture
def users():
    clear_v1()
    user = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    user_2 = auth_register_v2('anothervalidemail@gmail.com', '123abc!@#', 'Hayden', 'Smith')
    user_3 = auth_register_v2('yetanothervalidemail@gmail.com', '123abc!@#', 'Nothayden', 'Smith')
    return [user, user_2, user_3]

def test_one_user(users):
    new_dm = dm_create_v1(users[0]["token"], [])

    list_of_dms = dm_list_v1(users[0]["token"])["dms"]

    assert list_of_dms[0]["dm_id"] == new_dm["dm_id"]
    assert list_of_dms[0]["name"] == new_dm["dm_name"]

def test_other_user(users):
    new_dm = dm_create_v1(users[0]["token"], [users[1]["auth_user_id"], users[2]["auth_user_id"]])

    list_of_dms_1 = dm_list_v1(users[1]["token"])["dms"]
    list_of_dms_2 = dm_list_v1(users[2]["token"])["dms"]

    assert list_of_dms_1[0]["dm_id"] == new_dm["dm_id"]
    assert list_of_dms_1[0]["name"] == new_dm["dm_name"]

    assert list_of_dms_2[0]["dm_id"] == new_dm["dm_id"]
    assert list_of_dms_2[0]["name"] == new_dm["dm_name"]

def test_multiple_dms(users):
    new_dm = dm_create_v1(users[0]["token"], [users[1]["auth_user_id"]])
    new_dm_2 = dm_create_v1(users[2]["token"], [users[1]["auth_user_id"]])

    list_of_dms = dm_list_v1(users[1]["token"])["dms"]

    flag1 = False
    flag2 = False
    for dm in list_of_dms:
        if dm["dm_id"] == new_dm["dm_id"] and dm["name"] == new_dm["dm_name"]:
            flag1 = True
        if dm["dm_id"] == new_dm_2["dm_id"] and dm["name"] == new_dm_2["dm_name"]:
            flag2 = True
    
    assert flag1 == True and flag2 == True
    clear_v1()

