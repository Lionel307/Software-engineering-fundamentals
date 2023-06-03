import pytest

from src.channels import channels_create_v2
from src.channel import channel_details_v2 
from src.auth import auth_logout_v1, auth_register_v2
from src.error import InputError, AccessError
from src.other import clear_v1

@pytest.fixture
def auth_id():
    clear_v1()
    user_1 = auth_register_v2("hi@hi.com", "abcdefgh", "Hayden", "Smith")
    user_2 = auth_register_v2("hi2@hi.com", "abcdefgh", "Nothayden", "Smith")
    auth_ids = [user_1, user_2]

    return auth_ids

def test_correct_return_type(auth_id):
    
    c = channels_create_v2(auth_id[0]["token"], "test", True)
    assert isinstance(c, dict) == True
    assert isinstance(c["channel_id"], int) == True

def test_long_name(auth_id):
    
    with pytest.raises(InputError):
        channels_create_v2(auth_id[0]["token"], "abcdefghijklmnopqrstuvw", True)
    with pytest.raises(InputError):
        channels_create_v2(auth_id[0]["token"], "123456789112345678911", True)

def test_channel_created(auth_id):

    name = "test"
    channel = channels_create_v2(auth_id[0]["token"], name, True)

    details = channel_details_v2(auth_id[0]["token"], channel["channel_id"])

    assert details["name"] == name and details["owner_members"][0]["u_id"] == auth_id[0]["auth_user_id"]

def test_2_channels_created(auth_id):

    name1 = "test"
    channel_1 = channels_create_v2(auth_id[0]["token"], name1, True)

    name2 = "hello"
    channel_2 = channels_create_v2(auth_id[1]["token"], name2, True)

    detail_1 = channel_details_v2(auth_id[0]["token"], channel_1["channel_id"])

    assert detail_1["name"] == name1 and detail_1["owner_members"][0]["u_id"] == auth_id[0]["auth_user_id"]

    detail_2 = channel_details_v2(auth_id[1]["token"], channel_2["channel_id"])

    assert detail_2["name"] == name2 and detail_2["owner_members"][0]["u_id"] == auth_id[1]["auth_user_id"]

def test_logged_out_of_session(auth_id):

    auth_logout_v1(auth_id[0]["token"])

    with pytest.raises(AccessError):
        channels_create_v2(auth_id[0]["token"], "test", True)

def test_invalid_token(auth_id):

    with pytest.raises(AccessError):
        channels_create_v2("invalid_token", "test", True)

    with pytest.raises(AccessError):
        channels_create_v2([1, 2, 3], "test", True)

    with pytest.raises(AccessError):
        channels_create_v2(123456, "test", True)
    
    clear_v1()