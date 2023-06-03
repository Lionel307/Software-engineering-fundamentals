import pytest

from src.other import search_v2
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.channel import channel_join_v2
from src.message import message_send_v2, message_senddm_v1
from src.dm import dm_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1


@pytest.fixture
def users():
    '''
    Registers users for use in tests
    '''
    clear_v1()
    user_1 = auth_register_v2('validemail@gmail.com', '123abc!@#', 'M', 'J')
    user_2 = auth_register_v2('anothervalidemail@gmail.com', '123abc!@#', 'Hayden', 'Smith')
    user_3 = auth_register_v2('yetanothervalidemail@gmail.com', '123abc!@#', 'Nothayden', 'Smith')
    list_users = [user_1, user_2, user_3]

    return list_users


@pytest.fixture
def channels(users):
    '''
    Creates channels and adds a user 2 to channel 1 for use in tests
    '''
    dict_channel_id = channels_create_v2(users[0]["token"], "channel 1", True)
    dict_channel_id2 = channels_create_v2(users[1]["token"], "channel 2", True)
    channel_ids = [dict_channel_id['channel_id'], dict_channel_id2['channel_id']]

    channel_join_v2(users[1]['token'], channel_ids[0])

    return channel_ids


@pytest.fixture
def dms(users):
    '''
    Creates dms for use in tests
    '''
    dict_dm_id_1 = dm_create_v1(users[0]["token"], [users[1]['auth_user_id']])
    dm_id_1 = dict_dm_id_1['dm_id']
    dict_dm_id_2 = dm_create_v1(users[2]["token"], [users[1]['auth_user_id']])
    dm_id_2 = dict_dm_id_2['dm_id']

    dm_ids = [dm_id_1, dm_id_2]

    return dm_ids


@pytest.fixture
def c_message_ids(users, channels):
    '''
    Sends messages in channels for use in tests
    '''
    dict_c_message_1 = message_send_v2(users[0]["token"], channels[0], 'New message')
    c_message_1 = dict_c_message_1['message_id'] 
    
    dict_c_message_2 = message_send_v2(users[1]["token"], channels[0], 'another message')
    c_message_2 = dict_c_message_2['message_id']
    
    dict_c_message_3 = message_send_v2(users[1]["token"], channels[1], 'new channel new message')
    c_message_3 = dict_c_message_3['message_id']

    dict_c_message_4 = message_send_v2(users[1]["token"], channels[1], 'hi')
    c_message_4 = dict_c_message_4['message_id']

    channel_message_ids = [c_message_1, c_message_2, c_message_3, c_message_4]

    return channel_message_ids


@pytest.fixture
def d_message_ids(users, dms):
    '''
    Sends messages in channels for use in tests
    '''
    dict_d_message_1 = message_senddm_v1(users[0]["token"], dms[0], 'dm message')
    d_message_1 = dict_d_message_1['message_id']

    dict_d_message_2 = message_senddm_v1(users[1]["token"], dms[0], 'random message')
    d_message_2 = dict_d_message_2['message_id']

    dict_d_message_3 = message_senddm_v1(users[1]["token"], dms[1], 'new dm new message')
    d_message_3 = dict_d_message_3['message_id']

    dict_d_message_4 = message_senddm_v1(users[2]["token"], dms[1], 'hello')
    d_message_4 = dict_d_message_4['message_id']

    dm_message_ids = [d_message_1, d_message_2, d_message_3, d_message_4]

    return dm_message_ids


def test_no_dms_or_channels(users):
    '''
    A test which checks the output of the function when the user is not a part 
    of any dms or channels
    '''
    assert search_v2(users[0]["token"], "query_str") == {"messages": []}


def test_no_matches(users, c_message_ids, d_message_ids):
    '''
    A test which checks the output of the function when the user is part of channels
    and dms but no messages match query_str  
    '''
    assert search_v2(users[1]["token"], "query_str") == {"messages": []}


def test_matches(users, c_message_ids, d_message_ids):
    '''
    A test which checks the output of the function when the user is part of channels
    and dms and multiple messages match query_str
    '''
    matches = [c_message_ids[0], c_message_ids[1], c_message_ids[2], 
               d_message_ids[0], d_message_ids[1], d_message_ids[2]]

    output = search_v2(users[1]["token"], "message")
    output_messages = output['messages']

    matches_correct = True
    num_matches = 0
    for message in output_messages:
        if not message['message_id'] in matches:
            matches_correct = False

        if message['message_id'] in matches:
            num_matches += 1

    assert num_matches == len(matches)
    assert matches_correct == True


def test_invalid_query_str(users):
    '''
    A test which checks if an InputError is raised when query_str is above 1000 characters
    '''
    long_string = (
        "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, "
        "with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing "
        "in it to sit down on or to eat: it was a hobbit-hole, and that means comfort. It had a "
        "perfectly round door like a porthole, painted green, with a shiny yellow brass knob in " 
        "the exact middle. The door opened on to a tube-shaped hall like a tunnel: a very "
        "comfortable tunnel without smoke, with panelled walls, and floors tiled and carpeted, "
        "provided with polished chairs, and lots and lots of pegs for hats and coats - the "
        "hobbit was fond of visitors. The tunnel wound on and on, going fairly but not quite "
        "straight into the side of the hill - The Hill, as all the people for many miles round "
        "called it - and many little round doors opened out of it, first on one side and then "
        "on another. No going upstairs for the hobbit: bedrooms, bathrooms, cellars, "
        "pantries (lots of these), wardrobes (he had whole rooms devoted to clothes), kitchens, "
        "dining-rooms, all were on the same floor, and indeed on the same passage. The best rooms "
        "were all on the left-hand side (going in), for these were the only ones to have windows, "
        "deep-set round windows looking over his garden and meadows beyond, sloping down to the "
        "river."
    )

    with pytest.raises(InputError):
        search_v2(users[0]['token'], long_string)


def test_invalid_token():
    '''
    A test which checks if an AccessError is raised when the token passed in 
    is not a valid id
    '''
    with pytest.raises(AccessError):
        assert search_v2('', "query_str")

    with pytest.raises(AccessError):
        assert search_v2('invalid token', "query_str")

    with pytest.raises(AccessError):
        assert search_v2([1, 2, 3], "query_str")

    with pytest.raises(AccessError):
        assert search_v2((1, 2, 3), "query_str")

    with pytest.raises(AccessError):
        assert search_v2({}, "query_str")

    # To clear the persistent data file once all the tests have been executed
    clear_v1()
