'''
Tests for check_password()
'''
from password import check_password

def test_password():
    assert check_password("123456") == "Horrible password"
    assert check_password("cnb") == "Poor password"
    assert check_password("DUNDERmifflin21") == "Strong password"
    assert check_password("dreamtime64") == "Moderate password"
    assert check_password("3624738289") == "Moderate password"
    assert check_password("chicken") == "Poor password"
    assert check_password("35627&%&*$&") == "Moderate password"
    assert check_password("#$^&*$#%^&*(") == "Poor password"