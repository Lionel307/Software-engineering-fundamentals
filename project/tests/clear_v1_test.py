import pytest

from src.other import clear_v1
from src.error import InputError
from src.auth import auth_register_v1, auth_login_v1
from src.channel import channel_invite_v1
from src.channels import channels_create_v1, channels_listall_v1


# Adds userdata and checcks if clear_v1() resets it
def test_userdata_cleared():
    clear_v1()
    emails = ["hi@hi.com", "hola@hi.com", "bonjour@hi.com"]
    password = "abcdefghijk"
    first_name = "Hayden"
    last_name = "Smith"
    auth_register_v1(emails[0], password, first_name, last_name)
    auth_register_v1(emails[1], password, first_name, last_name)
    auth_register_v1(emails[2], password, first_name, last_name)

    clear_v1()

    with pytest.raises(InputError):
        auth_login_v1(emails[0], password)
    with pytest.raises(InputError):
        auth_login_v1(emails[1], password)
    with pytest.raises(InputError):
        auth_login_v1(emails[2], password)

  
# Adds channel data and checks if clear_v1() resets it to its initial state
def test_channeldata_cleared():
    clear_v1()

    a = auth_register_v1("hi@hi.com", "abcdefgh", "Hayden", "Smith")
    auth_id = a["auth_user_id"]

    initial = channels_listall_v1(auth_id)

    u = auth_register_v1("hola@hi.com", "abcdefgh", "Bob", "Bobson")
    u_id = u["auth_user_id"]

    c = channels_create_v1(auth_id, "test", True)
    channel_id = c["channel_id"]

    channel_invite_v1(auth_id, channel_id, u_id)

    clear_v1()
    
    a = auth_register_v1("hi@hi.com", "abcdefgh", "Hayden", "Smith")
    auth_id = a["auth_user_id"]
    
    final = channels_listall_v1(auth_id)

    assert initial == final

    clear_v1()
