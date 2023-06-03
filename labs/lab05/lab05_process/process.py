import json
import operator
import pickle

def process():
    with open('shapecolour.p', 'rb') as FILE:
        List = pickle.load(FILE)
    counter = 0
    num = List[0]
      
    for i in List:
        curr_frequency = List.count(i)
        if(curr_frequency > counter):
            counter = curr_frequency
            num = i

    DATA_STRUCTURE = {
        "mostCommon": {
            'colour': num['colour'],
            'shape': num['shape'],
        },
        "rawData": List,
    }
    
    with open('processed.json', 'w') as FILE:
        print(json.dumps(DATA_STRUCTURE))
        json.dump(DATA_STRUCTURE, FILE)

if __name__ == '__main__':
    process()