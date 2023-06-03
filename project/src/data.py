# How the data is supposed to look like once a program modifies the list.
# Changes (in the structure example below): 
#   removed the separate passwords list and added 'password' as another key in the users list of dictionaries
#   added 4 more keys to the channels list of dictionaries to include other data which requires storage

'''
users = [
    {
        'u_id': 12345,
        'email': 'xyz1@gmail.com',
        'name_first': 'user1_firstname',
        'name_last': 'user1_lastname',
        'handle_str': 'user1_firstnameuser1_lastname',
        'password': '12345@!#',
        'permission_id': 1,
    },
    {
        'u_id': 29385,
        'email': 'xyz2@gmail.com',
        'name_first': 'user2_firstname',
        'name_last': 'user2_lastname',
        'handle_str': 'user2_firstnameuser2_lastname',
        'password': '54321@!#',
        'permission_id': 2,
    },
]

channels = [
        {
            'id': 1,
            'name' : 'channel1',
            'is_public': True,
            'owner_members': [
                {
                'u_id': 29385,
                'email': 'xyz2@gmail.com',
                'name_first': 'user2_firstname',
                'name_last': 'user2_lastname',
                'handle_str': 'user2_firstnameuser2_lastname',
                },
            ],
            'all_members': [
                {
                'u_id': 29385,
                'email': 'xyz2@gmail.com',
                'name_first': 'user2_firstname',
                'name_last': 'user2_lastname',
                'handle_str': 'user2_firstnameuser2_lastname',
                },
            ],
            'messages': [
                {
                    'message_id': 123,
                    'u_id': 12345
                    'message': 'Hello World'
                    'time_created': 1445212800 # (unix timestamp)
                },
            ],  
        },
        {
            'id': 2,
            'name': 'channel2',
        },
]
'''

users = [

]

channels = [

]

dms = [

]

notifications = [

]

sessions = [

]

reset_codes = [

]