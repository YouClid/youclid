from flask import Flask, request, jsonify, render_template
import backend.main_parser
import json
import os

template_dir = os.path.abspath('./frontend')
static_dir = os.path.abspath('./frontend')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
name="postulate-1.json"

@app.route('/')
def hello():
    return render_template("index.html")

@app.route('/viewer')
def view():
   return render_template("viewer.html", name=name)

@app.route('/parse', methods=['POST'])
def parser():
    data = request.stream.read().decode()
    return json.dumps(backend.main_parser.parse(data.splitlines()))

if __name__ == '__main__':
    app.run(host="0.0.0.0")
