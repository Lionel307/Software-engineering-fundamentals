import pickle

def most_common():
    with open('shapecolour.p', 'rb') as FILE:
        List = pickle.load(FILE)
    counter = 0
    num = List[0]
      
    for i in List:
        curr_frequency = List.count(i)
        if(curr_frequency> counter):
            counter = curr_frequency
            num = i
    return num
