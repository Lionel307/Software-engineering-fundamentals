from list_exercises import *

def test_reverse():
    l = ["how", "are", "you"]
    reverse_list(l)
    assert l == ["you", "are", "how"]

def test_min_positive():
    assert minimum([1, 2, 3, 10]) == 1

def test_sum_positive():
    assert sum_list([7, 7, 7]) == 21

def test_max_positive():
    assert maximum([1, 2, 3, 10]) == 10

def test_sort_ascending():
    test_list = [32, 54, 8, 11]
    sort_ascending(test_list)
    assert test_list == [8, 11, 32, 54]
