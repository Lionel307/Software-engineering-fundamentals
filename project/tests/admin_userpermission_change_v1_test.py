import pytest

from src.auth import auth_register_v2, auth_logout_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.user import admin_userpermission_change_v1
from src.channels import channels_create_v2
from src.channel import channel_join_v2

@pytest.fixture
def users():
    clear_v1()
    user1 = auth_register_v2("hayden.smith@gmail.com", "Thisisastrongpassword123", "Hayden", "Smith")
    user2 = auth_register_v2("nothayden.smith@gmail.com", "Thisisastrongpassword123", "Nothayden", "Smith")
    user3 = auth_register_v2("definitelyhayden.smith@gmail.com", "Thisisastrongpassword123", "DefinitelyHayden", "Smith")

    return [user1, user2, user3]

# Creates a private channel to see if an user can join it.
@pytest.fixture
def testchannel(users):
    return channels_create_v2(users[0]["token"], "test", False)


def test_perms_changed(users, testchannel):

    admin_userpermission_change_v1(users[0]["token"], users[1]["auth_user_id"], 1)
    admin_userpermission_change_v1(users[0]["token"], users[2]["auth_user_id"], 1)

    channel_join_v2(users[0]["token"], testchannel["channel_id"])
    channel_join_v2(users[1]["token"], testchannel["channel_id"])
    channel_join_v2(users[2]["token"], testchannel["channel_id"])

def test_betrayal(users, testchannel):
    admin_userpermission_change_v1(users[0]["token"], users[1]["auth_user_id"], 1)
    admin_userpermission_change_v1(users[1]["token"], users[2]["auth_user_id"], 1)
    admin_userpermission_change_v1(users[2]["token"], users[0]["auth_user_id"], 2)


    channel_join_v2(users[1]["token"], testchannel["channel_id"])
    channel_join_v2(users[2]["token"], testchannel["channel_id"])

    with pytest.raises(AccessError):
        admin_userpermission_change_v1(users[0]["token"], users[1]["auth_user_id"], 2)

def test_invalid_u_id(users):
    clear_v1()
    user1 = auth_register_v2("hayden.smith@gmail.com", "Thisisastrongpassword123", "Hayden", "Smith")

    with pytest.raises(InputError):
        admin_userpermission_change_v1(user1["token"], users[1]["auth_user_id"], 1)

    with pytest.raises(InputError):
        admin_userpermission_change_v1(user1["token"], "abc", 1)

def test_wrong_permission_id(users):

    with pytest.raises(InputError):
        admin_userpermission_change_v1(users[0]["token"], users[1]["auth_user_id"], 0)
    
    for i in range(-42, 42):
        if i != 1 and i != 2:
            with pytest.raises(InputError):
                admin_userpermission_change_v1(users[0]["token"], users[1]["auth_user_id"], i)

def test_auth_user_not_owner(users):

    with pytest.raises(AccessError):
        admin_userpermission_change_v1(users[1]["token"], users[0]["auth_user_id"], 1)

    with pytest.raises(AccessError):
        admin_userpermission_change_v1(users[2]["token"], users[1]["auth_user_id"], 2)

def test_invalid_token(users):

    auth_logout_v1(users[0]["token"])
    with pytest.raises(AccessError):
        admin_userpermission_change_v1(users[0]["token"], users[1]["auth_user_id"], 1)

    with pytest.raises(AccessError):
        admin_userpermission_change_v1("invalid_token", users[1]["auth_user_id"], 1)

    with pytest.raises(AccessError):
        admin_userpermission_change_v1(42, users[1]["auth_user_id"], 1)
    clear_v1()