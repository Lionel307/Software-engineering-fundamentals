import pytest

from src.dm import dm_create_v1, dm_remove_v1, dm_list_v1
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
    assert dm_remove_v1(users[0]["token"], dm_id_1) == {}


def test_one_dm(users, dm_id_1):
    '''
    A test which checks if a dm is successfully removed when it is the only 
    DM in Dreams
    '''
    dm_remove_v1(users[0]["token"], dm_id_1)

    assert dm_list_v1(users[0]["token"]) == {"dms": []}


def test_multiple_dms(users, dm_id_1, dm_id_2):
    '''
    A test which checks if a dm is successfully removed and the other dms are unchanged
    when there are multiple DMs in Dreams 
    '''
    dm_remove_v1(users[0]["token"], dm_id_1)

    list_dms = dm_list_v1(users[0]["token"])
    list_dms = list_dms["dms"]
    
    dm_removed = True
    other_dm_present = False
    for dm in list_dms:
        if dm["dm_id"] == dm_id_1:
            dm_removed = False
        if dm["dm_id"] == dm_id_2:
            other_dm_present = True

    assert dm_removed == True and other_dm_present == True


def test_invalid_dm(users, dm_id_1):
    '''
    A test which checks if an InputError is raised when dm_id is not a valid dm
    '''
    with pytest.raises(InputError):
        assert dm_remove_v1(users[0]["token"], dm_id_1 + 1)

    with pytest.raises(InputError):
        assert dm_remove_v1(users[0]["token"], dm_id_1 + 2)

    with pytest.raises(InputError):
        assert dm_remove_v1(users[0]["token"], dm_id_1 + 3)


def test_not_creator(users, dm_id_1, dm_id_2):
    '''
    A test which checks if an AccessError is raised when the user trying to remove a dm
    is not the original creator of the dm
    '''
    with pytest.raises(AccessError):
        assert dm_remove_v1(users[1]["token"], dm_id_1)

    with pytest.raises(AccessError):
        assert dm_remove_v1(users[1]["token"], dm_id_2)

    with pytest.raises(AccessError):
        assert dm_remove_v1(users[2]["token"], dm_id_2)


def test_invalid_token(users, dm_id_1):
    '''
    A test which checks if an AccessError is raised when the token passed in 
    is not valid
    '''
    # invalidates the token of user 1
    auth_logout_v1(users[0]["token"])

    with pytest.raises(AccessError):
        assert dm_remove_v1(users[0]['token'], dm_id_1)

    with pytest.raises(AccessError):
        assert dm_remove_v1('', dm_id_1)

    with pytest.raises(AccessError):
        assert dm_remove_v1('invalid token', dm_id_1)

    with pytest.raises(AccessError):
        assert dm_remove_v1({}, dm_id_1)

    # To clear the persistent data file once all the tests have been executed
    clear_v1()
