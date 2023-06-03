import pytest

from src.auth import auth_passwordreset_request_v1, auth_passwordreset_reset_v1, auth_register_v2
from src.other import clear_v1
from src.error import InputError


def test_request_no_errors():
    clear_v1()
    # user doesn't exist doesn't return an error
    auth_passwordreset_request_v1("aFakeEmail89471987237@gmail.com")

    # User exists
    auth_register_v2("wed11b.echo@gmail.com", "qwerty123", "Lelouch", "Lamperouge")
    auth_passwordreset_request_v1("wed11b.echo@gmail.com")


def test_reset_invalid_code():
    clear_v1()
    with pytest.raises(InputError):
        auth_passwordreset_reset_v1("wrong_code", "thisisapassword")

def test_reset_short_password():
    clear_v1()
    with pytest.raises(InputError):
        auth_passwordreset_reset_v1("wrong_code", "p")
    clear_v1()