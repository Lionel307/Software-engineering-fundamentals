import pytest

from src.user import admin_user_remove_v1, admin_userpermission_change_v1
from src.user import user_profile_v2, users_all_v1
from src.auth import auth_register_v2, auth_login_v2
from src.channels import channels_create_v2
from src.channel import channel_messages_v2, channel_join_v2, channel_details_v2
from src.message import message_send_v2, message_senddm_v1
from src.dm import dm_create_v1, dm_messages_v1, dm_details_v1
from src.error import InputError, AccessError
from src.other import clear_v1


@pytest.fixture
def auth_users():
    '''
    Registers users for use in tests
    '''
    clear_v1()

    user_1 = auth_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    user_2 = auth_register_v2('random@gmail.com', '!@#123abc', 'Random', 'Name')
    user_3 = auth_register_v2('dj@gmail.com', '!@#123abc', 'Doris', 'Johnson')
    list_of_users = [user_1, user_2, user_3]
    
    return list_of_users


@pytest.fixture
def remove_user(auth_users):
    '''
    Removes a user from Dreams for use in tests
    '''
    output = admin_user_remove_v1(auth_users[0]['token'], auth_users[1]['auth_user_id'])

    return output


@pytest.fixture
def dm_id_1(auth_users):
    '''
    Creates a dm for use in tests
    '''
    new_dm = dm_create_v1(auth_users[0]["token"], [auth_users[1]['auth_user_id']])
    dm_id = new_dm["dm_id"]

    return dm_id


def test_correct_return(remove_user):
    '''
    A test which checks if the return value of the function is correct
    '''
    return_value = remove_user
    assert return_value == {}


def test_removed_user_login(auth_users, remove_user):
    '''
    A test which checks if an InputError is raised when a removed user
    tries to login
    '''
    with pytest.raises(InputError):
        auth_login_v2('random@gmail.com', '!@#123abc')


def test_removed_user_create_channel(auth_users, remove_user):
    '''
    A test which checks if an AccessError is raised when a removed user
    tries to create a channel
    '''
    with pytest.raises(AccessError):
        channels_create_v2(auth_users[1]['token'], 'new_channel', True)


def test_user_removed(auth_users, remove_user):
    '''
    A test which checks if the user has been successfully removed from Dreams
    '''
    all_users = users_all_v1(auth_users[2]['token'])
    list_users = all_users['users']

    is_removed = True
    for user in list_users:
        if user['u_id'] == auth_users[1]['auth_user_id']:
            is_removed = False

    assert is_removed == True


def test_owner_removed(auth_users):
    '''
    A test which checks if a Dreams owner has been successfully removed from Dreams
    '''
    admin_userpermission_change_v1(auth_users[0]['token'], auth_users[1]['auth_user_id'], 1)
    admin_user_remove_v1(auth_users[1]['token'], auth_users[0]['auth_user_id'])
    
    all_users = users_all_v1(auth_users[2]['token'])
    list_users = all_users['users']

    is_removed = True
    for user in list_users:
        if user['u_id'] == auth_users[0]['auth_user_id']:
            is_removed = False

    assert is_removed == True


def test_user_profile(auth_users, remove_user):
    '''
    A test which checks if the user profile is still retrievable with 
    user_profile_v2 (does not check the first name and last name
    is it is not well defined in the spec)
    '''
    r_user_profile = user_profile_v2(auth_users[2]['token'], auth_users[1]['auth_user_id'])
    r_user_profile = r_user_profile['user']

    assert r_user_profile['u_id'] == auth_users[1]['auth_user_id']
    assert r_user_profile['email'] == 'random@gmail.com'
    assert r_user_profile['handle_str'] == 'randomname'


def test_channel_messages_replaced(auth_users):
    '''
    A test which checks if the user's messages in a channel have been replaced 
    by "Removed user"
    '''
    dict_channel_id_1 = channels_create_v2(auth_users[0]["token"], 'channel_1', True)
    channel_id_1 = dict_channel_id_1['channel_id']

    channel_join_v2(auth_users[1]['token'], channel_id_1)

    message_send_v2(auth_users[1]['token'], channel_id_1, 'Hi')
    message_send_v2(auth_users[1]['token'], channel_id_1, 'Hello')
    message_send_v2(auth_users[1]['token'], channel_id_1, 'World')
    message_send_v2(auth_users[0]['token'], channel_id_1, 'Hey there')

    admin_user_remove_v1(auth_users[0]['token'], auth_users[1]['auth_user_id'])

    c_messages = channel_messages_v2(auth_users[0]['token'], channel_id_1, 0)
    list_messages = c_messages['messages']

    messages_removed = True
    for dict_message in list_messages:
        if not dict_message['message'] == 'Removed user' and \
        dict_message["u_id"] == auth_users[1]['auth_user_id']:
            messages_removed = False

    assert messages_removed == True


def test_removed_from_channel(auth_users):
    '''
    A test which checks if the user has been removed from the list of members and list of owners
    in a channel
    '''
    dict_channel_id_1 = channels_create_v2(auth_users[1]["token"], 'channel_1', True)
    channel_id_1 = dict_channel_id_1['channel_id']

    channel_join_v2(auth_users[0]['token'], channel_id_1)

    admin_user_remove_v1(auth_users[0]['token'], auth_users[1]['auth_user_id'])

    c_details = channel_details_v2(auth_users[0]['token'], channel_id_1)
    list_owners = c_details['owner_members']
    list_members = c_details['all_members']

    is_owner = False
    for owner in list_owners:
        if owner['u_id'] == auth_users[1]['auth_user_id']:
            is_owner = True

    is_member = False
    for member in list_members:
        if member['u_id'] == auth_users[1]['auth_user_id']:
            is_member = True

    assert is_owner == False
    assert is_member == False


def test_dm_messages_replaced(auth_users, dm_id_1):
    '''
    A test which checks if the user's messages in a dm have been replaced 
    by "Removed user"
    '''
    message_senddm_v1(auth_users[1]['token'], dm_id_1, 'Hi')
    message_senddm_v1(auth_users[1]['token'], dm_id_1, 'Hello')
    message_senddm_v1(auth_users[1]['token'], dm_id_1, 'World')
    message_senddm_v1(auth_users[0]['token'], dm_id_1, 'Hey there')

    admin_user_remove_v1(auth_users[0]['token'], auth_users[1]['auth_user_id'])

    dm_messages = dm_messages_v1(auth_users[0]['token'], dm_id_1, 0)
    list_messages = dm_messages['messages']

    messages_removed = True
    for dict_message in list_messages:
        if not dict_message['message'] == 'Removed user' and \
        dict_message["u_id"] == auth_users[1]['auth_user_id']:
            messages_removed = False

    assert messages_removed == True


def test_removed_from_dm(auth_users, dm_id_1):
    '''
    A test which checks if the user has been removed from the list of members in a dm
    '''
    admin_user_remove_v1(auth_users[0]['token'], auth_users[1]['auth_user_id'])

    d_details = dm_details_v1(auth_users[0]['token'], dm_id_1)
    list_members = d_details['members']

    is_member = False
    for member in list_members:
        if member['u_id'] == auth_users[1]['auth_user_id']:
            is_member = True

    assert is_member == False


def test_invalid_u_id(auth_users):
    '''
    A test which checks if an InputError is raised when the u_id does not
    refer to a valid user
    '''
    with pytest.raises(InputError):
        admin_user_remove_v1(auth_users[0]['token'], auth_users[2]['auth_user_id'] + 20000)

    with pytest.raises(InputError):
        admin_user_remove_v1(auth_users[0]['token'], {1, 2, 3})

    with pytest.raises(InputError):
        admin_user_remove_v1(auth_users[0]['token'], [194])


def test_only_owner(auth_users):
    '''
    A test which checks if an InputError is raised when the user is currently
    the only Dreams owner
    '''
    with pytest.raises(InputError):
        admin_user_remove_v1(auth_users[0]['token'], auth_users[0]['auth_user_id'])


def test_not_owner(auth_users):
    '''
    A test which checks if an AccessError is raised when the authorised user 
    is not a Dreams owner
    '''
    with pytest.raises(AccessError):
        admin_user_remove_v1(auth_users[1]['token'], auth_users[0]['auth_user_id'])

    with pytest.raises(AccessError):
        admin_user_remove_v1(auth_users[2]['token'], auth_users[0]['auth_user_id'])


def test_invalid_token(auth_users):
    '''
    A test which checks if an AccessError is raised when the token passed in 
    is not valid
    '''
    with pytest.raises(AccessError):
        admin_user_remove_v1('', auth_users[1]['auth_user_id'])

    with pytest.raises(AccessError):
        admin_user_remove_v1('invalid token', auth_users[1]['auth_user_id'])

    with pytest.raises(AccessError):
        admin_user_remove_v1([1, 2, 3], auth_users[1]['auth_user_id'])

    with pytest.raises(AccessError):
        admin_user_remove_v1({}, auth_users[1]['auth_user_id'])

    # To clear the persistent data file once all the tests have been executed
    clear_v1()
