import pytest

from src.user import users_all_v1
from src.auth import auth_register_v2
from src.other import clear_v1
from src.error import InputError, AccessError


@pytest.fixture
def user_1():
    '''
    Registers user number 1 for use in tests
    '''
    clear_v1()
    dict_user_1 = auth_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')

    return dict_user_1


@pytest.fixture
def user_2():
    '''
    Registers user number 2 for use in tests
    '''
    dict_user_2 = auth_register_v2('random@gmail.com', '!@#123abc', 'Random', 'Name')

    return dict_user_2


@pytest.fixture
def user_3():
    '''
    Registers user number 3 for use in tests
    '''
    dict_user_3 = auth_register_v2('dj@gmail.com', '!@#123abc', 'Doris', 'Johnson')

    return dict_user_3


def test_correct_return_type(user_1):
    '''
    A test which checks that the return type for the function is a dictionary
    '''
    list_of_users = users_all_v1(user_1['token'])

    assert isinstance(list_of_users, dict) == True


def test_single_user(user_1):
    '''
    A test which checks the output of the function when there is only 1 registered user
    '''
    expected_output = {
        'users': [
            {
                'u_id': user_1['auth_user_id'],
                'email': 'validemail@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Everest',
                'handle_str': 'haydeneverest'
            }
        ]
    }

    assert users_all_v1(user_1['token']) == expected_output


def test_multiple_users(user_1, user_2, user_3):
    '''
    A test which checks the output of the function when there are multiple registered users
    '''
    expected_output = {
        'users': [
            {
                'u_id': user_1['auth_user_id'],
                'email': 'validemail@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Everest',
                'handle_str': 'haydeneverest'
            },
            {
                'u_id': user_2['auth_user_id'],
                'email': 'random@gmail.com',
                'name_first': 'Random',
                'name_last': 'Name',
                'handle_str': 'randomname'
            },
            {
                'u_id': user_3['auth_user_id'],
                'email': 'dj@gmail.com',
                'name_first': 'Doris',
                'name_last': 'Johnson',
                'handle_str': 'dorisjohnson'
            }
        ]
    }

    assert users_all_v1(user_3['token']) == expected_output


def test_invalid_token():
    '''
    A test which checks if an AccessError is raised when the token passed in 
    is not valid
    '''
    with pytest.raises(AccessError):
        assert users_all_v1('')

    with pytest.raises(AccessError):
        assert users_all_v1('invalid token')

    with pytest.raises(AccessError):
        assert users_all_v1([1, 2, 3])

    with pytest.raises(AccessError):
        assert users_all_v1((1, 2, 3))

    with pytest.raises(AccessError):
        assert users_all_v1({})

    # To clear the persistent data file once all the tests have been executed
    clear_v1()
