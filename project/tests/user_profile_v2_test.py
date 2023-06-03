import pytest

from src.auth import auth_register_v2, auth_logout_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.channels import channels_create_v2
from src.user import user_profile_v2


def test_self():
    clear_v1()
    email = "hayden.smith@gmail.com"
    name_first = "Hayden"
    name_last = "Smith"
    handle = "haydensmith"

    user = auth_register_v2(email, "qwerty12345", name_first, name_last)

    profile = user_profile_v2(user["token"], user["auth_user_id"])["user"]

    assert profile["name_first"] == name_first
    assert profile["name_last"] == name_last
    assert profile["email"] == email
    assert profile["handle_str"] == handle
    assert profile["u_id"] == user["auth_user_id"]


def test_other_user_calls():
    clear_v1()
    email_1 = "hayden.smith@gmail.com"
    name_first_1 = "Hayden"
    name_last_1 = "Smith"
    handle_1 = "haydensmith"

    user_1 = auth_register_v2(email_1, "qwerty12345", name_first_1, name_last_1)

    email_2 = "holah@gmail.com"
    name_first_2 = "Hello"
    name_last_2 = "World"
    handle_2 = "helloworld"

    user_2 = auth_register_v2(email_2, "qwerty12345", name_first_2, name_last_2)

    profile_1 = user_profile_v2(user_2["token"], user_1["auth_user_id"])["user"]
    profile_2 = user_profile_v2(user_1["token"], user_2["auth_user_id"])["user"]

    assert profile_1["name_first"] == name_first_1
    assert profile_1["name_last"] == name_last_1
    assert profile_1["email"] == email_1
    assert profile_1["handle_str"] == handle_1
    assert profile_1["u_id"] == user_1["auth_user_id"]

    assert profile_2["name_first"] == name_first_2
    assert profile_2["name_last"] == name_last_2
    assert profile_2["email"] == email_2
    assert profile_2["handle_str"] == handle_2
    assert profile_2["u_id"] == user_2["auth_user_id"]


def test_many_registered():
    clear_v1()
    email = "hayden.smith@gmail.com"
    name_first = "Hayden"
    name_last = "Smith"
    handle = "haydensmith"

    auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello2@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello3@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello4@gmail.com", "qwerty12345", "Hi", "World")
    user = auth_register_v2(email, "qwerty12345", name_first, name_last)
    auth_register_v2("hello5@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello6@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello7@gmail.com", "qwerty12345", "Hi", "World")
    auth_register_v2("hello8@gmail.com", "qwerty12345", "Hi", "World")

    profile = user_profile_v2(user["token"], user["auth_user_id"])["user"]
    assert profile["name_first"] == name_first
    assert profile["name_last"] == name_last
    assert profile["email"] == email
    assert profile["handle_str"] == handle
    assert profile["u_id"] == user["auth_user_id"]


def test_user_does_not_exist():
    clear_v1()

    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")
    
    with pytest.raises(InputError):
        user_profile_v2(user["token"], 42)


def test_invalid_token():
    clear_v1()

    user = auth_register_v2("hello1@gmail.com", "qwerty12345", "Hi", "World")

    with pytest.raises(AccessError):
        user_profile_v2(2, user["auth_user_id"])

    with pytest.raises(AccessError):
        user_profile_v2('hello', user["auth_user_id"])

    auth_logout_v1(user["token"])
    with pytest.raises(AccessError):
        user_profile_v2(user["token"], user["auth_user_id"])
    clear_v1()