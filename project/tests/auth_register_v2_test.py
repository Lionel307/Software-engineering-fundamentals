import pytest

from src.auth import auth_login_v2, auth_register_v2
from src.error import InputError, AccessError
from src.other import clear_v1
from src.channels import channels_create_v2


@pytest.fixture
def valid_emails():
    emails = ['validemail@gmail.com', 'ANOTHERVALIDEMAIL@gmail.com', 'yetAnothervalidEMAIL@gmail.com']
    return emails

@pytest.fixture
def long_name():
    long_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return long_string

@pytest.fixture
def auth_ids(valid_emails):
    clear_v1()

    auth_id_1 = auth_register_v2(valid_emails[0], '123abc!@#', 'Hayden', 'Everest')
    auth_id_2 = auth_register_v2(valid_emails[1], '453gkw!@#', 'Michelle', 'Anderson')
    auth_id_3 = auth_register_v2(valid_emails[2], '538ryg!@#', 'Jeremy', 'Cooper')
    list_of_ids = [auth_id_1["auth_user_id"], auth_id_2["auth_user_id"], auth_id_3["auth_user_id"]]

    return list_of_ids

def test_valid_register(valid_emails, auth_ids):
    u = auth_login_v2(valid_emails[0], '123abc!@#')
    u_id = u["auth_user_id"]
    assert u_id == auth_ids[0]
    u = auth_login_v2(valid_emails[1], '453gkw!@#')
    u_id = u["auth_user_id"]
    assert u_id == auth_ids[1]
    u = auth_login_v2(valid_emails[2], '538ryg!@#')
    u_id = u["auth_user_id"]
    assert u_id == auth_ids[2]


def test_invalid_email():
    with pytest.raises(InputError):
        assert auth_register_v2('wrong$$$Email@gmail.com', '123abc!@#', 'Hayden', 'Everest')

    with pytest.raises(InputError):
        assert auth_register_v2('wrongEmail!!@gmail.com', '453gkw!@#', 'Michelle', 'Anderson')

    with pytest.raises(InputError):
        assert auth_register_v2('wrongEmail@@gmail.com', '538ryg!@#', 'Jeremy', 'Cooper')


def test_repeated_email(valid_emails, auth_ids):
    with pytest.raises(InputError):
        assert auth_register_v2(valid_emails[0], '4392dw@!#', 'Felix', 'Cruz')

    with pytest.raises(InputError):
        assert auth_register_v2(valid_emails[1], '4727@*wiej', 'Mars', 'Thompson')

    with pytest.raises(InputError):
        assert auth_register_v2(valid_emails[2], '5@282!asdj', 'Chris', 'Jackson')


def test_short_password(valid_emails):
    clear_v1()

    with pytest.raises(InputError):
        assert auth_register_v2(valid_emails[0], 'ab2#', 'Hayden', 'Everest')

    with pytest.raises(InputError):
        assert auth_register_v2(valid_emails[1], '5@8', 'Michelle', 'Anderson')
    
    with pytest.raises(InputError):
        assert auth_register_v2(valid_emails[2], '1', 'Jeremy', 'Cooper')


def test_short_password_edgeCases(valid_emails):
    clear_v1()

    with pytest.raises(InputError):
        assert auth_register_v2(valid_emails[0], 'p!wr#', 'Hayden', 'Everest')

    with pytest.raises(InputError):
        assert auth_register_v2(valid_emails[1], '', 'Michelle', 'Anderson')


def test_invalid_name_first(valid_emails, long_name):
    clear_v1()

    with pytest.raises(InputError):
        assert auth_register_v2(valid_emails[0], '123abc!@#', '', 'Everest')

    with pytest.raises(InputError):
        assert auth_register_v2(valid_emails[1], '453gkw!@#', long_name, 'Anderson')


def test_invalid_name_last(valid_emails, long_name):
    clear_v1()

    with pytest.raises(InputError):
        assert auth_register_v2(valid_emails[0], '123abc!@#', 'Hayden', '')

    with pytest.raises(InputError):
        assert auth_register_v2(valid_emails[1], '453gkw!@#', 'Michelle', long_name)

def test_token_works(valid_emails, long_name):
    clear_v1()
    user = auth_register_v2(valid_emails[0], "Password824378234", "Hayden", "Smith")

    channels_create_v2(user["token"], "hello", True)


def test_same_names(valid_emails):
    clear_v1()
    auth_register_v2(valid_emails[0], "Password824378234", "Haydenhayden", "Smithsmith")
    auth_register_v2(valid_emails[1], "Password824378234", "Haydenhayden", "Smithsmith")
    auth_register_v2(valid_emails[2], "Password824378234", "Haydenhayden", "Smithsmith")

    auth_login_v2(valid_emails[0], 'Password824378234')
    auth_login_v2(valid_emails[1], 'Password824378234')
    auth_login_v2(valid_emails[2], 'Password824378234')

    clear_v1()
