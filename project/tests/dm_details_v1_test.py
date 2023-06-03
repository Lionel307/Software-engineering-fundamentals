import pytest
from src.dm import dm_create_v1, dm_details_v1
from src.auth import auth_register_v2
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
def dm_1(users):
    '''
    Creates dm 1 for use in tests
    '''
    dm_1 = dm_create_v1(users[0]['token'], [users[1]['auth_user_id']])

    return dm_1


def test_two_members(users, dm_1):
    '''
    A test which checks the output when there are 2 members in a dm
    '''
    DM_NAME = dm_1['dm_name']
    DM_ID = dm_1['dm_id']

    expected_output = {
        'name': DM_NAME,
        'members': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'validemail@gmail.com',
                'name_first': 'M',
                'name_last': 'J',
                'handle_str': 'mj'
            }, 
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'anotheremail@gmail.com',
                'name_first': 'A',
                'name_last': 'I',
                'handle_str': 'ai'
            },
        ],
    }

    assert dm_details_v1(users[0]['token'], DM_ID) == expected_output
    assert dm_details_v1(users[1]['token'], DM_ID) == expected_output


def test_multiple_members(users):
    '''
    A test which checks the output when there are more than 2 members in a dm
    '''
    new_dm = dm_create_v1(users[0]['token'], [users[1]['auth_user_id'], users[2]['auth_user_id']])
    DM_NAME = new_dm['dm_name']
    DM_ID = new_dm['dm_id']

    expected_output = {
        'name': DM_NAME,
        'members': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'validemail@gmail.com',
                'name_first': 'M',
                'name_last': 'J',
                'handle_str': 'mj'
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'anotheremail@gmail.com',
                'name_first': 'A',
                'name_last': 'I',
                'handle_str': 'ai'
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'random@gmail.com',
                'name_first': 'R',
                'name_last': 'N',
                'handle_str': 'rn'
            },
        ],
    }

    assert dm_details_v1(users[0]['token'], DM_ID) == expected_output
    assert dm_details_v1(users[1]['token'], DM_ID) == expected_output
    assert dm_details_v1(users[2]['token'], DM_ID) == expected_output


def test_invalid_dm(users, dm_1):
    '''
    A test which checks if an InputError is raised when dm_id is not a valid dm
    '''
    with pytest.raises(InputError):
        dm_details_v1(users[0]['token'], dm_1['dm_id'] + 1)

    with pytest.raises(InputError):
        dm_details_v1(users[0]['token'], dm_1['dm_id'] + 2)

    with pytest.raises(InputError):
        dm_details_v1(users[0]['token'], dm_1['dm_id'] + 3)


def test_auth_not_member(users, dm_1):
    '''
    A test which checks if an AccessError is raised when the authorised user
    is not a member of the dm with dm_id
    '''
    with pytest.raises(AccessError):
        dm_details_v1(users[2]['token'], dm_1['dm_id'])


def test_invalid_token(users, dm_1):
    '''
    A test which checks if an AccessError is raised when the token passed in 
    is not valid
    '''
    with pytest.raises(AccessError):
        dm_details_v1('', dm_1['dm_id'])

    with pytest.raises(AccessError):
        dm_details_v1('invalid token', dm_1['dm_id'])

    with pytest.raises(AccessError):
        dm_details_v1(1, dm_1['dm_id'])

    with pytest.raises(AccessError):
        dm_details_v1((1, 2, 3), dm_1['dm_id'])

    with pytest.raises(AccessError):
        dm_details_v1({}, dm_1['dm_id'])

    # To clear the persistent data file once all the tests have been executed
    clear_v1()
