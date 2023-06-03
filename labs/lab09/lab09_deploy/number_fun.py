import typing

def multiply_by_two(number):
    '''
    Multiplies a given number by two.
    '''
    return number*2

def print_message(message):
    '''
    Prints a given message.
    '''
    print(f"{message}")

def sum_list_of_numbers(numbers):
    '''
    Returns the sum of a list of numbers
    '''
    return sum(numbers)

def sum_iterable_of_numbers(numbers):
    '''
    Calculates the sum of an iterable of numbers

    numbers: any iterable

    Return value: integer
    '''
    return sum(numbers)


def is_in(needle, haystack):
    '''
    Checks if the given item is in a list
    
    Parameters:
    - needle: a string or an integer
    - haystack: a list of strings or integers

    Return value: bool - if the needle is in the haystack
    '''
    for value in haystack:
        if needle == value:
            return True

def index_of_number(item, numbers):
    '''
    Returns the index of the given item in a list of numbers

    Parameters:
    - item: an integer
    - numbers: a list of numbers

    Return value: the index of the item, or None if the items is not in numbers
    '''
    for i, num in enumerate(numbers):
        if item == num:
            return i
    return None

