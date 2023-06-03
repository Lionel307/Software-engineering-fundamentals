import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1


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

    auth_id_1 = auth_register_v1(valid_emails[0], '123abc!@#', 'Hayden', 'Everest')
    auth_id_2 = auth_register_v1(valid_emails[1], '453gkw!@#', 'Michelle', 'Anderson')
    auth_id_3 = auth_register_v1(valid_emails[2], '538ryg!@#', 'Jeremy', 'Cooper')
    list_of_ids = [auth_id_1, auth_id_2, auth_id_3]
    
    return list_of_ids


def test_valid_register(valid_emails, auth_ids):
    assert auth_login_v1(valid_emails[0], '123abc!@#') == auth_ids[0]
    assert auth_login_v1(valid_emails[1], '453gkw!@#') == auth_ids[1]
    assert auth_login_v1(valid_emails[2], '538ryg!@#') == auth_ids[2]


def test_invalid_email():
    with pytest.raises(InputError):
        assert auth_register_v1('wrong$$$Email@gmail.com', '123abc!@#', 'Hayden', 'Everest')

    with pytest.raises(InputError):
        assert auth_register_v1('wrongEmail!!@gmail.com', '453gkw!@#', 'Michelle', 'Anderson')

    with pytest.raises(InputError):
        assert auth_register_v1('wrongEmail@@gmail.com', '538ryg!@#', 'Jeremy', 'Cooper')


def test_repeated_email(valid_emails, auth_ids):
    with pytest.raises(InputError):
        assert auth_register_v1(valid_emails[0], '4392dw@!#', 'Felix', 'Cruz')

    with pytest.raises(InputError):
        assert auth_register_v1(valid_emails[1], '4727@*wiej', 'Mars', 'Thompson')

    with pytest.raises(InputError):
        assert auth_register_v1(valid_emails[2], '5@282!asdj', 'Chris', 'Jackson')


def test_short_password(valid_emails):
    clear_v1()

    with pytest.raises(InputError):
        assert auth_register_v1(valid_emails[0], 'ab2#', 'Hayden', 'Everest')

    with pytest.raises(InputError):
        assert auth_register_v1(valid_emails[1], '5@8', 'Michelle', 'Anderson')
    
    with pytest.raises(InputError):
        assert auth_register_v1(valid_emails[2], '1', 'Jeremy', 'Cooper')


def test_short_password_edgeCases(valid_emails):
    clear_v1()

    with pytest.raises(InputError):
        assert auth_register_v1(valid_emails[0], 'p!wr#', 'Hayden', 'Everest')

    with pytest.raises(InputError):
        assert auth_register_v1(valid_emails[1], '', 'Michelle', 'Anderson')


def test_invalid_name_first(valid_emails, long_name):
    clear_v1()

    with pytest.raises(InputError):
        assert auth_register_v1(valid_emails[0], '123abc!@#', '', 'Everest')

    with pytest.raises(InputError):
        assert auth_register_v1(valid_emails[1], '453gkw!@#', long_name, 'Anderson')


def test_invalid_name_last(valid_emails, long_name):
    clear_v1()

    with pytest.raises(InputError):
        assert auth_register_v1(valid_emails[0], '123abc!@#', 'Hayden', '')

    with pytest.raises(InputError):
        assert auth_register_v1(valid_emails[1], '453gkw!@#', 'Michelle', long_name)

def test_long_many_long_handles(valid_emails):
    auth_register_v1(valid_emails[0], '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1(valid_emails[1], '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1(valid_emails[2], '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello1@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello2@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello3@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello4@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello5@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello6@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello7@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello8@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello9@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello10@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello11@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello12@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello13@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello14@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')
    auth_register_v1("hello15@hi.com", '123abc!@#', 'Haydenhayden', 'Everesteverest')

    auth_login_v1(valid_emails[0], '123abc!@#')
    auth_login_v1(valid_emails[1], '123abc!@#')
    auth_login_v1(valid_emails[2], '123abc!@#')