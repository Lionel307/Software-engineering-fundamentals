def roman(numerals):
    '''
    Given Roman numerals as a string, return their value as an integer. You may
    assume the Roman numerals are in the "standard" form, i.e. any digits
    involving 4 and 9 will always appear in the subtractive form.

    For example:
    >>> roman("II")
    2
    >>> roman("IV")
    4
    >>> roman("IX")
    9
    >>> roman("XIX")
    19
    >>> roman("XX")
    20
    >>> roman("MDCCLXXVI")
    1776
    >>> roman("MMXIX")
    2019
    '''
    integer = 0
    i = 0
    # break up the roman numerals to compare them in pairs
    while i < len(numerals):
        rom_num_1 = rom_value(numerals[i])
        if (i + 1) < len(numerals):
            rom_num_2 = rom_value(numerals[i + 1])
            # if the first numeral is greater than the next, add normally
            if (rom_num_1 >= rom_num_2):
                integer += rom_num_1
                i += 1
            # the next numeral is greater than the current numeral ie IV
            else:
                integer += (rom_num_2 - rom_num_1)
                i += 2
        else:
            integer += rom_num_1
            i += 1

    return integer

def rom_value(r):
    if (r == 'I'):
        return 1
    if (r == 'V'):
        return 5
    if (r == 'X'):
        return 10
    if (r == 'L'):
        return 50
    if (r == 'C'):
        return 100
    if (r == 'D'):
        return 500
    if (r == 'M'):
        return 1000
    return -1


