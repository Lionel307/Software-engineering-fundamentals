from count import count_char

def test_empty():
    assert count_char("") == {}

def test_simple():
    assert count_char("abc") == {"a": 1, "b": 1, "c": 1}

def test_double():
    assert count_char("aa") == {"a": 2}

def test_uppercase():
    assert count_char("XyZ") == {"X": 1, "y": 1, "Z": 1}

def test_long():
    assert count_char("Rapapapa") == {"R": 1, "a": 4, "p": 3}
