import pytest

from src.auth import auth_login_v1, auth_register_v1
from src.error import InputError
from src.other import clear_v1


@pytest.fixture
def valid_emails():
    emails = ['validemail@gmail.com', 'ANOTHERVALIDEMAIL@gmail.com', 'yetAnothervalidEMAIL@gmail.com']
    return emails


@pytest.fixture
def auth_ids(valid_emails):
    clear_v1()

    auth_id_1 = auth_register_v1(valid_emails[0], '123abc!@#', 'Hayden', 'Everest')
    auth_id_2 = auth_register_v1(valid_emails[1], '453gkw!@#', 'Michelle', 'Anderson')
    auth_id_3 = auth_register_v1(valid_emails[2], '538ryg!@#', 'Jeremy', 'Cooper')
    list_of_ids = [auth_id_1, auth_id_2, auth_id_3]
    
    return list_of_ids


def test_valid_login(valid_emails, auth_ids):
    assert auth_login_v1(valid_emails[0], '123abc!@#') == auth_ids[0]
    assert auth_login_v1(valid_emails[1], '453gkw!@#') == auth_ids[1]
    assert auth_login_v1(valid_emails[2], '538ryg!@#') == auth_ids[2]


def test_invalid_emails():
    with pytest.raises(InputError):
        assert auth_login_v1('wrong$$$Email@gmail.com', '123abcd!@#')

    with pytest.raises(InputError):
        assert auth_login_v1('wrongEmail!!@gmail.com', '12345')

    with pytest.raises(InputError):
        assert auth_login_v1('wrongEmail@@gmail.com', '58294@#')


def test_unregistered_emails(valid_emails):
    clear_v1()

    with pytest.raises(InputError):
        assert auth_login_v1(valid_emails[0], '123abc!@#')
    
    with pytest.raises(InputError):
        assert auth_login_v1(valid_emails[1], '453gkw!@#')
    
    with pytest.raises(InputError):
        assert auth_login_v1(valid_emails[2], '538ryg!@#')


def test_wrong_password(valid_emails, auth_ids):
    with pytest.raises(InputError):
        assert auth_login_v1(valid_emails[0], 'wrongPassword')
    
    with pytest.raises(InputError):
        assert auth_login_v1(valid_emails[1], 'wrongPassword')
    
    with pytest.raises(InputError):
        assert auth_login_v1(valid_emails[2], 'wrongPassword')
