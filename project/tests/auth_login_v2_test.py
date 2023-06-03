import pytest

from src.auth import auth_login_v2, auth_register_v2
from src.error import InputError
from src.other import clear_v1
from src.channel import channel_join_v2
from src.channels import channels_create_v2


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


def test_valid_login(valid_emails, auth_ids):
    auth_id_1 = auth_ids[0]["auth_user_id"]
    auth_id_2 = auth_ids[1]["auth_user_id"]
    auth_id_3 = auth_ids[2]["auth_user_id"]
    assert auth_login_v2(valid_emails[0], '123abc!@#')["auth_user_id"] == auth_id_1
    assert auth_login_v2(valid_emails[1], '453gkw!@#')["auth_user_id"] == auth_id_2
    assert auth_login_v2(valid_emails[2], '538ryg!@#')["auth_user_id"] == auth_id_3


def test_invalid_emails():
    with pytest.raises(InputError):
        assert auth_login_v2('wrong$$$Email@gmail.com', '123abcd!@#')

    with pytest.raises(InputError):
        assert auth_login_v2('wrongEmail!!@gmail.com', '12345')

    with pytest.raises(InputError):
        assert auth_login_v2('wrongEmail@@gmail.com', '58294@#')


def test_unregistered_emails(valid_emails):
    clear_v1()

    with pytest.raises(InputError):
        assert auth_login_v2(valid_emails[0], '123abc!@#')
    
    with pytest.raises(InputError):
        assert auth_login_v2(valid_emails[1], '453gkw!@#')
    
    with pytest.raises(InputError):
        assert auth_login_v2(valid_emails[2], '538ryg!@#')


def test_wrong_password(valid_emails, auth_ids):
    with pytest.raises(InputError):
        assert auth_login_v2(valid_emails[0], 'wrongPassword')
    
    with pytest.raises(InputError):
        assert auth_login_v2(valid_emails[1], 'wrongPassword')
    
    with pytest.raises(InputError):
        assert auth_login_v2(valid_emails[2], 'wrongPassword')

def test_token_works(valid_emails, auth_ids):

    user_1 = auth_login_v2(valid_emails[0], '123abc!@#')
    channel_id = channels_create_v2(user_1["token"], "hello", True)
    channel_join_v2(user_1["token"], channel_id["channel_id"])


def test_multiple_tokens_work(valid_emails, auth_ids):

    user_1 = auth_login_v2(valid_emails[0], '123abc!@#')
    user_2 = auth_login_v2(valid_emails[1], '453gkw!@#')
    user_3 = auth_login_v2(valid_emails[2], '538ryg!@#')

    channel_id = channels_create_v2(user_1["token"], "hello", True)

    channel_join_v2(user_1["token"], channel_id["channel_id"])

    channel_join_v2(user_2["token"], channel_id["channel_id"])

    channel_join_v2(user_3["token"], channel_id["channel_id"])

    clear_v1()
