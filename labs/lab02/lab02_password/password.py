def check_password(password):
    '''
    Takes in a password, and returns a string based on the strength of that password.

    The returned value should be:
    * "Strong password", if at least 12 characters, contains at least one number, at least one uppercase letter, at least one lowercase letter.
    * "Moderate password", if at least 8 characters, contains at least one number.
    * "Poor password", for anything else
    * "Horrible password", if the user enters "password", "iloveyou", or "123456"
    '''
    length = 0
    number = False
    uppercase = False
    lowercase = False

    if password is "password" or password is "iloveyou" or password is "123456":
        return "Horrible password"
        
    for i in password:
        if i.isdigit():
            number = True
        if i.islower():
            lowercase = True
        if i.isupper():
            uppercase = True
        length += 1

    if length >= 12 and number and uppercase and lowercase:
        return "Strong password"
    elif length >= 8 and number:
        return "Moderate password"
    else:
        return "Poor password"

    

if __name__ == '__main__':
    print(check_password("ihearttrimesters"))
    # What does this do?
