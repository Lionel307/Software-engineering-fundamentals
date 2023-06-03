import pytest
import requests
import json

from src.config import url

def test_request_no_errors():
    requests.delete(url + "clear/v1")

    # user doesn't exist doesn't return an error
    assert requests.post(url + "auth/passwordreset/request/v1", json={"email": "aFakeEmail89471987237@gmail.com"}).status_code == 200

    requests.post(url + "auth/register/v2", json={
        "email": "wed11b.echo@gmail.com", "password": "123abc!@", "name_first": "Lelouch", "name_last": "Lamperouge" 
    })

    assert requests.post(url + "auth/passwordreset/request/v1", json={"email": "wed11b.echo@gmail.com"}).status_code == 200

def test_reset_invalid_code_short_password():
    requests.delete(url + "clear/v1")

    assert requests.post(url + "auth/passwordreset/reset/v1", json={
        "reset_code": "wrong_code", "new_password": "thisisapassword"
    }).status_code == 400

    assert requests.post(url + "auth/passwordreset/reset/v1", json={
        "reset_code": "wrong_code", "new_password": "p"
    }).status_code == 400

    requests.delete(url + "clear/v1")
