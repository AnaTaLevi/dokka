import json
from flask import Flask, request
import service

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/getAddresses', methods=['POST'])
def get_address():
    file = request.files['file'].read()
    res = service.file_to_json(file)

    return json.dumps(res)


@app.route('/getResult', methods=['GET'])
def get_result():
    uuid = request.args['uuid']
    res = service.get_result(uuid)

    return json.dumps(res)


if __name__ == '__main__':
    app.run(debug=True)
