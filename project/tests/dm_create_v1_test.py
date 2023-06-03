import pytest

from src.auth import auth_register_v2
from src.dm import dm_create_v1, dm_list_v1
from src.error import InputError, AccessError
from src.other import clear_v1

@pytest.fixture
def user_1():
    clear_v1()
    token_1 = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    return token_1

@pytest.fixture
def user_2():
    token_2 = auth_register_v2('anotheremail@gmail.com', 'abc!@#123', 'N', 'A')
    return token_2

@pytest.fixture
def user_3():
    token_3 = auth_register_v2('randnomemail@gmail.com', '!@#123abc', 'A', 'B')
    return token_3

# test one dm
def test_return(user_1, user_2):
    u_ids = [user_2['auth_user_id']]
    dm = dm_create_v1(user_1['token'], u_ids)
    dm_name = dm['dm_name']
    dm_id = dm['dm_id']

    dm = dm_list_v1(user_1['token'])
    dm_list = dm['dms']

    flag = 0
    for a in dm_list:
        if a['dm_id'] == dm_id and a['name'] == dm_name:
            flag = 1
    assert flag == 1

#test creating multiple dms
def test_multiple_dms(user_1, user_2, user_3):
    u_ids = [user_2['auth_user_id']]
    dm = dm_create_v1(user_1['token'], u_ids)
    dm_id_1 = dm['dm_id']
    u_ids = [user_2['auth_user_id'], user_3['auth_user_id']]
    dm = dm_create_v1(user_1['token'], u_ids)
    dm_id_2 = dm['dm_id']

    dm = dm_list_v1(user_1['token'])
    dm_list = dm['dms']
    names = ['mj, na', 'ab, mj, na']
    flag = [False, False]

    for a in dm_list:
        if a['dm_id'] == dm_id_1 and a['name'] == names[0]:
            flag[0] = True
    for a in dm_list:
        if a['dm_id'] == dm_id_2 and a['name'] == names[1]:
            flag[1] = True

    for a in flag:
        assert flag[a] == True    

def test_invalid_user(user_1, user_2):
    with pytest.raises(InputError):
        assert dm_create_v1(user_1['token'], [user_2['auth_user_id'] + 1])

def test_invalid_token(user_1, user_2):
    with pytest.raises(AccessError):
        assert dm_create_v1("Invalid_token", [user_2['auth_user_id']])

    clear_v1()
