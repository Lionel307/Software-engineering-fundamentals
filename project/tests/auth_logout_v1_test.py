import pytest

from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channels import channels_create_v2
from src.error import AccessError
from src.other import clear_v1

@pytest.fixture
def valid_emails():
    emails = ['validemail@gmail.com', 'ANOTHERVALIDEMAIL@gmail.com', 'yetAnothervalidEMAIL@gmail.com']
    return emails


@pytest.fixture
def auth_ids(valid_emails):
    clear_v1()

    auth_id_1 = auth_register_v2(valid_emails[0], '123abc!@#', 'Hayden', 'Everest')
    auth_id_2 = auth_register_v2(valid_emails[1], '453gkw!@#', 'Michelle', 'Anderson')
    auth_id_3 = auth_register_v2(valid_emails[2], '538ryg!@#', 'Jeremy', 'Cooper')
    list_of_ids = [auth_id_1, auth_id_2, auth_id_3]

    return list_of_ids

def test_logout_returns_success(auth_ids):

    assert auth_logout_v1(auth_ids[0]["token"])["is_success"] == True
    assert auth_logout_v1(auth_ids[1]["token"])["is_success"] == True
    assert auth_logout_v1(auth_ids[2]["token"])["is_success"] == True

def test_logout_invalidates_token(auth_ids):

    assert auth_logout_v1(auth_ids[0]["token"])["is_success"] == True
    assert auth_logout_v1(auth_ids[1]["token"])["is_success"] == True
    assert auth_logout_v1(auth_ids[2]["token"])["is_success"] == True

    with pytest.raises(AccessError):
        channels_create_v2(auth_ids[0]["token"], "hello", True)

    with pytest.raises(AccessError):
        channels_create_v2(auth_ids[1]["token"], "hello", True)

    with pytest.raises(AccessError):
        channels_create_v2(auth_ids[2]["token"], "hello", True)

def test_logout_then_login_then_logout_invalidates_token(auth_ids, valid_emails):

    assert auth_logout_v1(auth_ids[0]["token"])["is_success"] == True
    assert auth_logout_v1(auth_ids[1]["token"])["is_success"] == True
    assert auth_logout_v1(auth_ids[2]["token"])["is_success"] == True

    user_1 = auth_login_v2(valid_emails[0], '123abc!@#')
    user_2 = auth_login_v2(valid_emails[1], '453gkw!@#')
    user_3 = auth_login_v2(valid_emails[2], '538ryg!@#')

    assert auth_logout_v1(user_1["token"])["is_success"] == True
    assert auth_logout_v1(user_2["token"])["is_success"] == True
    assert auth_logout_v1(user_3["token"])["is_success"] == True

    with pytest.raises(AccessError):
        channels_create_v2(user_1["token"], "hello", True)

    with pytest.raises(AccessError):
        channels_create_v2(user_2["token"], "hello", True)

    with pytest.raises(AccessError):
        channels_create_v2(user_3["token"], "hello", True)



def test_invalid_token():

    with pytest.raises(AccessError):
        auth_logout_v1("invalid_token")["is_success"]
    with pytest.raises(AccessError):
        auth_logout_v1([1, 2, 3])["is_success"]
    with pytest.raises(AccessError):
        auth_logout_v1({'user_1': 1})["is_success"]

def test_valid_token_not_logged_in(auth_ids):

    auth_logout_v1(auth_ids[0]["token"])
    auth_logout_v1(auth_ids[1]["token"])
    auth_logout_v1(auth_ids[2]["token"])

    with pytest.raises(AccessError):
        auth_logout_v1(auth_ids[0]["token"])["is_success"]
    with pytest.raises(AccessError):
        auth_logout_v1(auth_ids[1]["token"])["is_success"]
    with pytest.raises(AccessError):
        auth_logout_v1(auth_ids[2]["token"])["is_success"]

    clear_v1()