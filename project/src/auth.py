import re
import hashlib
import jwt
from uuid import uuid4
import os
import smtplib
from email.mime.text import MIMEText
from .error import InputError, AccessError
from .data import users, sessions, reset_codes
import src.other

EMAIL_ADDRESS = "wed11b.echo@gmail.com"
EMAIL_PASSWORD = "comp1531t121WED11BECHO"


def auth_login_v1(email, password):
    '''
    Given a registered user's email and password and returns their 'auth_user_id' value

    Arguments:
        email :: [str] - The user's email address.
        password :: [str] - The user's password.
    
    Exceptions:
        InputError - Occurs when:
            - Email entered is not a valid email
            - Email entered does not belong to a user
            - Password is not correct
    
    Return Value:
        Returns the user's auth_user_id in a dictionary
    '''

    # Regular expression for validating an Email
    regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'
    if not re.search(regex, email):
        raise InputError(description="Invalid Email")

    u_id = False
    for user in users:
        if user['email'] == email and user['password'] == password:
            u_id = user['u_id']

    if u_id == False:
        raise InputError(description="Invalid details")

    return {
        'auth_user_id': u_id,
    }


def auth_register_v1(email, password, name_first, name_last):
    '''
    Given a user's first and last name, email address, and password, create a new
    account for them and return a new `auth_user_id`. A handle is generated that is
    the concatenation of a lowercase-only first name and last name. If the concatenation
    is longer than 20 characters, it is cutoff at 20 characters. The handle will not include
    any whitespace or the '@' character. If the handle is already taken, append the
    concatenated names with the smallest number (starting at 0) that forms a new handle
    that isn't already taken. The addition of this final number may result in the handle
    exceeding the 20 character limit.

    Arguments:
        email :: [str] - The user's email address.
        password :: [str] - The user's password.
        name_first :: [str] - The user's first name
        name_last :: [str] - The user's last name

    Exceptions:
        InputError - Occurs when:
            - Email entered is not a valid email
            - Email address is already being used by another user
            - Password entered is less than 6 characters long
            - name_first is not between 1 and 50 characters inclusively in length
            - name_last is not between 1 and 50 characters inclusively in length
    
    Return Value:
        Returns a new auth_user_id assigned to the registered user in a dictionary
    '''

    # Regular expression for validating an Email
    regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'
    if not re.search(regex, email):
        raise InputError(description="Invalid Email")

    if len(password) < 6:
        raise InputError(description="Password must be more than 6 characters long")


    if(len(name_first) < 1 or len(name_first) > 50 or len(name_last) < 1 or len(name_last) > 50):
        raise InputError(description="First last names must each be >0 and <51 characters long")

    for user in users:
        if user['email'] == email:
            raise InputError(description="Email address already in use")

    l_first = name_first.lower()
    l_first = l_first.replace(' ', '')
    l_first = l_first.replace('@', '')
    l_last = name_last.lower()
    l_last = l_last.replace(' ', '')
    l_last = l_last.replace('@', '')
    handle = l_first + l_last

    if len(handle) > 20:
        handle = handle[:20]

    flag = False
    for user in users:
        if user['handle_str'] == handle:
            flag = True

    count = 0
    p_handle = handle
    while flag == True:
        flag = False
        if len(p_handle) >= 20:
            length = 20 - len(str(count))
            handle = p_handle[:length]
        p_handle = handle + str(count)

        for user in users:
            if user['handle_str'] == p_handle:
                flag = True
                count = count + 1

    handle = p_handle
    u_id = len(users) + 1

    if u_id == 1:
        permission_id = 1
    else:
        permission_id = 2

    new_user = {
        'u_id': u_id,
        'email': email,
        'name_first': name_first,
        'name_last': name_last,
        'handle_str': handle,
        'password': password,
        'permission_id': permission_id,
    }

    users.append(new_user)

    return {
        'auth_user_id': u_id,
    }


def auth_register_v2(email, password, name_first, name_last):
    '''
Given a user's first and last name, email address, and password, 
creates a new account for them and returns a new `token` for that session.

    Arguments:
        email :: [str] - The user's email address.
        password :: [str] - The user's password.
        name_first :: [str] - The user's first name
        name_last :: [str] - The user's last name
    
    Exceptions:
        InputError - Occurs when:
            - Email entered is not a valid email
            - Email address is already being used by another user
            - Password entered is less than 6 characters long
            - name_first is not between 1 and 50 characters inclusively in length
            - name_last is not between 1 and 50 characters inclusively in length
    
    Return Value:
        Returns a new session token and a new auth_user_id assigned to the registered user in a dictionary 
    '''

    # Regular expression for validating an Email
    regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'
    if not re.search(regex, email):
        raise InputError(description="Invalid Email")

    if len(password) < 6:
        raise InputError(description="Password must be more than 6 characters long")

    if(len(name_first) < 1 or len(name_first) > 50 or len(name_last) < 1 or len(name_last) > 50):
        raise InputError(description="First last names must each be >0 and <51 characters long")

    if name_first == "Removed" and name_last == "user":
        raise InputError(description="Name cannot be Removed user")

    for user in users:
        if user['email'].lower() == email.lower() and not \
        (user["name_first"] == "Removed" and user["name_last"] == "user"):
            raise InputError(description="Email address already in use")

    l_first = name_first.lower()
    l_first = l_first.replace(' ', '')
    l_first = l_first.replace('@', '')
    l_last = name_last.lower()
    l_last = l_last.replace(' ', '')
    l_last = l_last.replace('@', '')
    handle = l_first + l_last

    if len(handle) > 20:
        handle = handle[:20]

    flag = False
    for user in users:
        if user['handle_str'] == handle:
            flag = True

    count = 0
    p_handle = handle
    while flag == True:
        flag = False
        if len(p_handle) >= 20:
            length = 20 - len(str(count))
            handle = p_handle[:length]
        p_handle = handle + str(count)

        for user in users:
            if user['handle_str'] == p_handle:
                flag = True
                count = count + 1

    handle = p_handle
    u_id = len(users) + 1

    if u_id == 1:
        permission_id = 1
    else:
        permission_id = 2

    # Salts and Hashes the password
    salt = hashlib.sha256(os.urandom(60)).hexdigest()

    password = password + salt
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    new_user = {
        'u_id': u_id,
        'email': email,
        'name_first': name_first,
        'name_last': name_last,
        'handle_str': handle,
        'password_hash': password_hash,
        'permission_id': permission_id,
        'salt': salt
    }

    users.append(new_user)

    # Generates a token for the user
    secret = src.other.get_secret()
    session_id = uuid4().hex
    token = jwt.encode({"session_id": session_id}, secret, algorithm="HS256")

    # Adds the session id to the list of logged in users
    session_details = {
        "session_id": session_id,
        "u_id": u_id
    }
    sessions.append(session_details)

    # Write temp data to json file for persistence
    src.other.update_data_write()

    return {
        "token": token,
        "auth_user_id": u_id,
    }


def auth_login_v2(email, password):
    '''
    Given a registered user's email and password and returns their 'auth_user_id' value

    Arguments:
        email :: [str] - The user's email address.
        password :: [str] - The user's password.
    
    Exceptions:
        InputError - Occurs when:
            - Email entered is not a valid email
            - Email entered does not belong to a user
            - Password is not correct
    
    Return Value:
        Returns the user's auth_user_id and a new session token in a dictionary
    '''

    # Regular expression for validating an Email
    regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'
    if not re.search(regex, email):
        raise InputError(description="Invalid Email")

    email = email.lower()
    salt = False
    for user in users:
        if user['email'].lower() == email:
            salt = user['salt']
            name_first = user['name_first']
            name_last = user['name_last']

    if salt == False:
        raise InputError(description="Invalid details")

    password = password + salt
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    u_id = False
    for user in users:
        if user['email'].lower() == email and user['password_hash'] == password_hash:
            u_id = user['u_id']

    if u_id == False:
        raise InputError(description="Invalid details")

    if name_first == "Removed" and name_last == "user":
        raise InputError(description="Invalid details")

    # Generates a token for the user
    secret = src.other.get_secret()
    session_id = uuid4().hex
    token = jwt.encode({"session_id": session_id}, secret, algorithm="HS256")

    # Adds the session id to the list of logged in users
    session_details = {
        "session_id": session_id,
        "u_id": u_id
    }
    sessions.append(session_details)

    # Write temp data to json file for persistence
    src.other.update_data_write()

    return {
        "token": token,
        "auth_user_id": u_id,
    }


def auth_logout_v1(token):
    '''
    Given an active token, invalidates the token to log the user out. If a valid token is given, 
    and the user is successfully logged out, it returns true, otherwise false.

    Arguments:
        token :: [str] - current session token
    
    Exceptions:
        N/A
    
    Return Value:
        {is_success} where the value of is_success is a bool.
        Returns True if user is successfully logged out, else returns False
    '''

    secret = src.other.get_secret()

    # Raises AccessError if the decoding fails due to signature error
    try:
        decoded = jwt.decode(token, secret, algorithms=['HS256'])
    except Exception:
        raise AccessError(description="Invalid token") from Exception

    session_id = decoded["session_id"]
    logged_in = False
    new_session_list = []
    for user in sessions:
        if user["session_id"] != session_id:
            new_session_list.append(user)
        else:
            logged_in = True

    if logged_in == False:
        raise AccessError(description="Not logged in")

    # This rebuilds the sessions list without the logged out user
    sessions.clear()
    sessions.extend(new_session_list)

    src.other.update_data_write()
    return {
        "is_success": True
    }

def auth_passwordreset_request_v1(email):
    '''
    Given an email address, if the user is a registered user, sends them an email containing a 
    specific secret code, that when entered in auth_passwordreset_reset, shows that the user 
    trying to reset the password is the one who got sent this email.

    Arguments:
        email :: [str] - email address of the user attempting to reset their password
    
    Exceptions:
        N/A
    
    Return Value:
        {}
    '''

    u_id = False
    for user in users:
        if user["email"] == email:
            u_id = user["u_id"]
    
    if u_id == False:
        return {}

    code = (uuid4().hex)[:16]
    # Salts and Hashes the password
    salt = hashlib.sha256(os.urandom(60)).hexdigest()
    code_hash = code + salt
    code_hash = hashlib.sha256(code_hash.encode()).hexdigest()

    msg = MIMEText(f"Your reset code is: {code}")
    msg["subject"] = "Password Reset for UNSW Dreams"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

    mail = smtplib.SMTP("smtp.gmail.com", 587)
    mail.ehlo()
    mail.starttls()
    mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    mail.sendmail(EMAIL_ADDRESS, email, msg.as_string())
    mail.close()

    reset_codes.append({
        "u_id": u_id,
        "code": code_hash,
        "salt": salt
    })
    src.other.update_data_write()
    return {
    }

def auth_passwordreset_reset_v1(reset_code, new_password):
    '''
    Given a reset code for a user, set that user's new password to the password provided

    Arguments:
        reset_code :: [str] - email address of the user attempting to reset their password
        new_password :: [str] - the new password to change the current one to
    
    Exceptions:
        InputError - Occurs when:
            - reset_code is not a valid reset code
            - Password entered is less than 6 characters long
    
    Return Value:
        {}
    '''
    if len(new_password) < 6:
        raise InputError(description="Password must be more than 6 characters long")

    u_id = False
    for code in reset_codes:
        hashed_code = hashlib.sha256((reset_code + code["salt"]).encode()).hexdigest()
        if code["code"] == hashed_code:
            u_id = code["u_id"]
            reset_codes.remove(code)

    if u_id == False:
        raise InputError(description="Invalid Reset Code")

    # Salts and Hashes the password
    salt = hashlib.sha256(os.urandom(60)).hexdigest()
    password = new_password + salt
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    for user in users:
        if user["u_id"] == u_id:
            user["password_hash"] = password_hash
            user["salt"] = salt
    src.other.update_data_write()
    return {
    }