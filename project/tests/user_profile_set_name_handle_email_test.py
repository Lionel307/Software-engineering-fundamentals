import pytest

from src.auth import auth_register_v2, auth_logout_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.channels import channels_create_v2
from src.channel import channel_details_v2, channel_join_v2
from src.dm import dm_create_v1, dm_details_v1
from src.user import user_profile_v2, user_profile_setname_v2, user_profile_setemail_v2, user_profile_sethandle_v1

def test_set_name_valid():
    clear_v1()
    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")

    name_first = "Hayden"
    name_last = "Smith"
    user_profile_setname_v2(user["token"], name_first, name_last)

    profile = user_profile_v2(user["token"], user["auth_user_id"])["user"]

    assert profile["name_first"] == name_first
    assert profile["name_last"] == name_last


# To make sure the correct user is modified when there are many users
def test_set_name_many_registered():
    clear_v1()
    name_first = "Hayden"
    name_last = "Smith"

    auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello2@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello3@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello4@gmail.com", "qwerty12345", "Hi", "World")
    user = auth_register_v2("hi@gmail.com", "qwerty12345", "Hello", "World")
    auth_register_v2("hello5@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello6@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello7@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello8@gmail.com", "qwerty12345", "Hi", "World")

    user_profile_setname_v2(user["token"], name_first, name_last)
    profile = user_profile_v2(user["token"], user["auth_user_id"])["user"]
    assert profile["name_first"] == name_first
    assert profile["name_last"] == name_last

def test_set_name_invalid_name():
    clear_v1()
    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")
    name_first = "Hayden"
    name_last = "Smith"
    long_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    with pytest.raises(InputError):
        user_profile_setname_v2(user["token"], long_string, name_last)

    with pytest.raises(InputError):
        user_profile_setname_v2(user["token"], name_first, long_string)

    with pytest.raises(InputError):
        user_profile_setname_v2(user["token"], long_string, long_string)

    with pytest.raises(InputError):
        user_profile_setname_v2(user["token"], "", name_last)

    with pytest.raises(InputError):
        user_profile_setname_v2(user["token"], name_first, "")


def test_set_name_invalid_token():
    clear_v1()
    name_first = "Hayden"
    name_last = "Smith"

    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")

    with pytest.raises(AccessError):
        user_profile_setname_v2("hello", name_first, name_last)

    with pytest.raises(AccessError):
        user_profile_setname_v2(42, name_first, name_last)

    auth_logout_v1(user["token"])
    with pytest.raises(AccessError):
        user_profile_setname_v2(user["token"], name_first, name_last)


def test_set_email_valid():
    clear_v1()
    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")
    email = "hayden.smith@gmail.com"
    user_profile_setemail_v2(user["token"], email)
    profile = user_profile_v2(user["token"], user["auth_user_id"])["user"]
    assert profile["email"] == email

def test_set_email_many_registered():
    clear_v1()

    auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello2@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello3@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello4@gmail.com", "qwerty12345", "Hi", "World")
    user = auth_register_v2("hi@gmail.com", "qwerty12345", "Hello", "World")
    auth_register_v2("hello5@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello6@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello7@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello8@gmail.com", "qwerty12345", "Hi", "World")

    email = "hayden.smith@gmail.com"
    user_profile_setemail_v2(user["token"], email)
    profile = user_profile_v2(user["token"], user["auth_user_id"])["user"]
    assert profile["email"] == email

def test_set_email_invalid_email():
    clear_v1()
    invalid_email = ["wrong$$$Email@gmail.com", "wrongEmail!!@gmail.com", "wrongEmail@@gmail.com"]

    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hello", "World")
    with pytest.raises(InputError):
        user_profile_setemail_v2(user["token"], invalid_email[0])
    with pytest.raises(InputError):
        user_profile_setemail_v2(user["token"], invalid_email[1])
    with pytest.raises(InputError):
        user_profile_setemail_v2(user["token"], invalid_email[2])

def test_set_email_in_use():
    clear_v1()
    email = "hayden.smith@gmail.com"

    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hello", "World")
    auth_register_v2(email, "qwerty12345", "Hello", "World")

    with pytest.raises(InputError):
        user_profile_setemail_v2(user["token"], email)

def test_set_email_invalid_token():
    clear_v1()
    email = "hayden.smith@gmail.com"

    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")

    with pytest.raises(AccessError):
        user_profile_setemail_v2("hello", email)

    with pytest.raises(AccessError):
        user_profile_setemail_v2(42, email)

    auth_logout_v1(user["token"])
    with pytest.raises(AccessError):
        user_profile_setemail_v2(user["token"], email)

def test_set_handle_valid():
    clear_v1()
    handle = "hello"

    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")
    user_profile_sethandle_v1(user["token"], handle)
    profile = user_profile_v2(user["token"], user["auth_user_id"])["user"]
    assert profile["handle_str"] == handle

def test_set_handle_many_registered():
    clear_v1()

    auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello2@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello3@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello4@gmail.com", "qwerty12345", "Hi", "World")
    user = auth_register_v2("hi@gmail.com", "qwerty12345", "Hello", "World")
    auth_register_v2("hello5@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello6@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello7@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello8@gmail.com", "qwerty12345", "Hi", "World")

    handle = "hello"
    user_profile_sethandle_v1(user["token"], handle)
    profile = user_profile_v2(user["token"], user["auth_user_id"])["user"]
    assert profile["handle_str"] == handle

def test_set_handle_invalid_length():
    clear_v1()
    invalid_handle = ["", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "hi"]

    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hello", "World")
    with pytest.raises(InputError):
        user_profile_sethandle_v1(user["token"], invalid_handle[0])
    with pytest.raises(InputError):
        user_profile_sethandle_v1(user["token"], invalid_handle[1])
    with pytest.raises(InputError):
        user_profile_sethandle_v1(user["token"], invalid_handle[2])

def test_set_handle_in_use():
    clear_v1()
    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hello", "World")
    auth_register_v2("hello2@gmail.com", "qwerty12345", "Hayden", "Smith")

    with pytest.raises(InputError):
        user_profile_sethandle_v1(user["token"], "haydensmith")

def test_set_handle_invalid_token():
    clear_v1()
    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")

    with pytest.raises(AccessError):
        user_profile_sethandle_v1("hello", "haydensmith")

    with pytest.raises(AccessError):
        user_profile_sethandle_v1(42, "haydensmith")

    auth_logout_v1(user["token"])
    with pytest.raises(AccessError):
        user_profile_sethandle_v1(user["token"], "haydensmith")

def test_set_updates_channel_and_dm_data():
    clear_v1()

    name_first = "Hayden"
    name_last = "Smith"
    email = "hayden.smith@gmail.com"
    handle = "haydenisgreat123"

    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")

    channel_id = channels_create_v2(user["token"], "test", True)["channel_id"]
    dm_id = dm_create_v1(user["token"], [])["dm_id"]


    user_profile_setname_v2(user["token"], name_first, name_last)
    user_profile_sethandle_v1(user["token"], handle)
    user_profile_setemail_v2(user["token"], email)

    channel_details = channel_details_v2(user["token"], channel_id)
    dm_details = dm_details_v1(user["token"], dm_id)

    assert channel_details["owner_members"][0]["email"] == email
    assert channel_details["owner_members"][0]["handle_str"] == handle
    assert channel_details["owner_members"][0]["name_first"] == name_first
    assert channel_details["owner_members"][0]["name_last"] == name_last

    assert channel_details["all_members"][0]["email"] == email
    assert channel_details["all_members"][0]["handle_str"] == handle
    assert channel_details["all_members"][0]["name_first"] == name_first
    assert channel_details["all_members"][0]["name_last"] == name_last

    assert dm_details["members"][0]["email"] == email
    assert dm_details["members"][0]["handle_str"] == handle
    assert dm_details["members"][0]["name_first"] == name_first
    assert dm_details["members"][0]["name_last"] == name_last

def test_another_for_channel_and_dm():
    clear_v1()

    name_first = "Hayden"
    name_last = "Smith"
    email = "hayden.smith@gmail.com"
    handle = "haydenisgreat123"

    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")
    user1 =auth_register_v2("hello2@gmail.com", "qwerty12345", "Hi", "World")
    user2 = auth_register_v2("hello3@gmail.com", "qwerty12345", "Hi", "World")
    user3 = auth_register_v2("hello4@gmail.com", "qwerty12345", "Hi", "World")

    channel_id = channels_create_v2(user["token"], "test", True)["channel_id"]
    dm_id = dm_create_v1(user["token"], [user1["auth_user_id"], user2["auth_user_id"], user3["auth_user_id"],])["dm_id"]

    channel_join_v2(user1["token"], channel_id)
    channel_join_v2(user2["token"], channel_id)
    channel_join_v2(user3["token"], channel_id)

    user_profile_setname_v2(user2["token"], name_first, name_last)
    user_profile_sethandle_v1(user2["token"], handle)
    user_profile_setemail_v2(user2["token"], email)
    
    channel_details = channel_details_v2(user["token"], channel_id)
    dm_details = dm_details_v1(user["token"], dm_id)

    this_user = 0
    for member in dm_details["members"]:
        if member["u_id"] == user2["auth_user_id"]:
            this_user = member
    assert this_user["email"] == email
    assert this_user["handle_str"] == handle
    assert this_user["name_first"] == name_first
    assert this_user["name_last"] == name_last

    for member in channel_details["all_members"]:
        if member["u_id"] == user2["auth_user_id"]:
            this_user = member

    assert this_user["email"] == email
    assert this_user["handle_str"] == handle
    assert this_user["name_first"] == name_first
    assert this_user["name_last"] == name_last


    clear_v1()
