from roman import *
def test():
    assert roman("II") == 2
    assert roman("IV") == 4
    assert roman("IX") == 9
    assert roman("XIX") == 19
def test2():
    assert roman("XX") == 20
    assert roman("MDCCLXXVI") == 1776
    assert roman("MMXIX") == 2019
    assert roman("MMMCMXCIX") == 3999
    assert roman("CDXCIV") == 494
