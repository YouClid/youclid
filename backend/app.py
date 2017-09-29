from flask import Flask, request, jsonify
from main_parser import parse
import json

app = Flask(__name__)

@app.route('/parse', methods=['POST'])
def hello():
    data = request.stream.read().decode()
    return jsonify(parse(data.splitlines()))

if __name__ == '__main__':
    app.run()
