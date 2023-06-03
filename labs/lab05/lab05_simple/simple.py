from flask import Flask, request
from json import dumps

app = Flask(__name__)

data = {
    'name':[],
}

def getData():
    global data
    return data


@app.route("/name/add", methods=['POST'])
def add():
    data = getData()
    name = request.form.get('name')
    data['name'].append(name)
    return dumps({})

@app.route("/names", methods=['GET'])
def get_name():
    data = getData()
    return dumps(data)

@app.route("/name/remove", methods=['DELETE'])
def remove():
    data = getData()
    del_name = request.form.get('name')
    data['name'].remove(del_name)
    return dumps({})



# Write your routes here

if __name__ == '__main__':
    app.run(port=0)