import pytest

from src.dm import dm_create_v1, dm_leave_v1, dm_list_v1, dm_details_v1
from src.auth import auth_register_v2, auth_logout_v1
from src.error import AccessError, InputError
from src.other import clear_v1


@pytest.fixture
def users():
    '''
    Registers users for use in tests
    '''
    clear_v1()

    user_1 = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    user_2 = auth_register_v2('anotheremail@gmail.com', '!@#123abc', 'A', 'I')
    user_3 = auth_register_v2('random@gmail.com', '!@#123abc', 'R', 'N')
    list_of_users = [user_1, user_2, user_3]
    
    return list_of_users


@pytest.fixture
def dm_id_1(users):
    '''
    Creates dm 1 for use in tests
    '''
    new_dm = dm_create_v1(users[0]["token"], [users[1]["auth_user_id"]])
    dm_id = new_dm['dm_id']

    return dm_id


@pytest.fixture
def dm_id_2(users):
    '''
    Creates dm 2 for use in tests
    '''
    new_dm = dm_create_v1(users[0]["token"], [users[1]["auth_user_id"], users[2]["auth_user_id"]])
    dm_id = new_dm['dm_id']
    
    return dm_id


def test_correct_return(users, dm_id_1):
    '''
    A test which checks if the return value of the function is correct
    '''
    assert dm_leave_v1(users[1]["token"], dm_id_1) == {}


def test_user_left(users, dm_id_1):
    '''
    A test which checks if the user has successfully left the DM
    '''
    dm_leave_v1(users[1]["token"], dm_id_1)

    user_2_dms = dm_list_v1(users[1]["token"])

    user_left = True
    if not user_2_dms == {"dms": []}:
        user_left = False

    dm_1_details = dm_details_v1(users[0]["token"], dm_id_1)
    dm_1_members = dm_1_details["members"]

    for member in dm_1_members:
        if member["u_id"] == users[1]["auth_user_id"]:
            user_left = False

    assert user_left == True


def test_other_dms_unchanged(users, dm_id_1, dm_id_2):
    '''
    A test which checks that the other dms of the user remain unchanged after
    leaving a dm
    '''
    dm_leave_v1(users[1]["token"], dm_id_1)

    user_2_dms = dm_list_v1(users[1]["token"])
    user_2_dms = user_2_dms["dms"]

    dm_2_in_list = False
    if  user_2_dms[0]["dm_id"] == dm_id_2:
        dm_2_in_list = True

    dm_2_details = dm_details_v1(users[1]["token"], dm_id_2)
    dm_2_members = dm_2_details["members"]

    in_dm_2 = False
    for member in dm_2_members:
        if member["u_id"] == users[1]["auth_user_id"]:
            in_dm_2 = True

    assert dm_2_in_list == True and in_dm_2 == True


def test_other_members_unchanged(users, dm_id_2):
    '''
    A test which checks if other members of a dm remain unchanged after the user
    leaves that dm
    '''
    dm_leave_v1(users[1]["token"], dm_id_2)

    dm_2_details = dm_details_v1(users[0]["token"], dm_id_2)
    dm_2_members = dm_2_details["members"]

    user_1_present = False
    user_2_left = True
    user_3_present = False

    for member in dm_2_members:
        if member["u_id"] == users[0]["auth_user_id"]:
            user_1_present = True

        if member["u_id"] == users[2]["auth_user_id"]:
            user_3_present = True

        if member["u_id"] == users[1]["auth_user_id"]:
            user_2_left = False

    assert user_1_present == True and user_2_left == True and user_3_present == True


def test_invalid_dm(users, dm_id_1):
    '''
    A test which checks if an InputError is raised when dm_id is not a valid dm
    '''
    with pytest.raises(InputError):
        dm_leave_v1(users[1]["token"], dm_id_1 + 1)

    with pytest.raises(InputError):
        dm_leave_v1(users[1]["token"], dm_id_1 + 2)

    with pytest.raises(InputError):
        dm_leave_v1(users[1]["token"], dm_id_1 + 3)


def test_auth_not_member(users, dm_id_1, dm_id_2):
    '''
    A test which checks if an AccessError is raised when the authorised user
    is not a member of the dm with dm_id
    '''
    dm_leave_v1(users[1]["token"], dm_id_1)
    dm_leave_v1(users[1]["token"], dm_id_2)

    with pytest.raises(AccessError):
        dm_leave_v1(users[1]["token"], dm_id_1)

    with pytest.raises(AccessError):
        dm_leave_v1(users[1]["token"], dm_id_2)

    with pytest.raises(AccessError):
        dm_leave_v1(users[2]["token"], dm_id_1)


def test_invalid_token(users, dm_id_1):
    '''
    A test which checks if an AccessError is raised when the token passed in 
    is not valid
    '''
    # invalidates the token of user 1
    auth_logout_v1(users[1]["token"])

    with pytest.raises(AccessError):
        dm_leave_v1(users[1]['token'], dm_id_1)

    with pytest.raises(AccessError):
        dm_leave_v1('', dm_id_1)

    with pytest.raises(AccessError):
        dm_leave_v1('invalid token', dm_id_1)

    with pytest.raises(AccessError):
        dm_leave_v1({}, dm_id_1)

    # To clear the persistent data file once all the tests have been executed
    clear_v1()
