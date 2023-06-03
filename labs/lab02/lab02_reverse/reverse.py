def reverse_words(string_list):
    '''
    Given a list of strings, return a new list where the order of the words is
    reversed
    '''
    new = []
    for string in string_list:
        if string is not ' ':
            s = string.split()
            s.reverse()
            new.append(' '.join(s))
        else:
            new.append(string) 
	        
    return new
    pass

if __name__ == "__main__": 
    print(reverse_words(["Hello World", "I am here"]))
    # it should print ['World Hello', 'here am I']
