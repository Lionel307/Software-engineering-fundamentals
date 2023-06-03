## auth.py
### auth_register_v1
* Interpreted the spec as saying the concatenation of numbers to the end of the handle may result in the handle exceeding the 20 character limit, therefore I must account for it by removing letters.
* A user can not register with the first and last names as "Removed user". It will raise an InputError if it is attempted.

### auth_logout_v1
* For auth_logout_v1, no exception is raised when an invalid token is used and that False is returned instead. Spec says that AccessError is thrown when invalid token is passed in but description for logout implies that no exception is raised and instead, False is returned.

## channel.py
### channel_join_v1
* Function does nothing and does not output an error message if the user is already a member of the channel.

### channel_invite_v1
* Function does nothing and does not output an error message if the user is already a member of the channel.

### channel_messages_v1
* When returning messages between index start and end it returns the message at 'start' but not at index 'end' 
as that would result in it returning 51 messages.

### channel_addowner_v1
* Raises an InputError when the u_id passed in is not a member of channel with channel_id

## message.py
### message_send_v2
* Raises an InputError if the channel specified does not exist.

### message_senddm_v1
* Raises an InputError if the dm specified does not exist.

### message_share_v1
* The format for the shared message is f"{new_message}:\n  \"\"\n  {og_message}\n  \"\""
* When a message is shared to a different channel the user_id for the message posted belongs to the user who shared the message
* The new message combined with the shared message cannot exceed 1000 characters in length. It will raise an InputError if it does.
* shared_message_id will be a new message id
* If the message with og_message_id is in a channel that the auth_user is not a part of, AccessError will be raised unless the auth_user is a global owner

## other.py
* Logged in sessions get reset when the server restarts. This means that session data does not persist.

## user.py
### admin_user_remove_v1
* When a user is removed, it will replace both their first name and last name as "Removed user".

### admin_userpermission_change_v1
* Dreams owners are able to change their own permission_id

## dm.py
## dm_create_v1
* A notification is sent not only when a user is invited to the dm but also when a dm is created with them in it.

### dm_invite_v1
* Function does nothing and does not output an error message if the user is already a member of the dm.
