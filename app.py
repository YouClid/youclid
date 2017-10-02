from flask import Flask, request, jsonify, render_template
import backend.main_parser
import json
import os

template_dir = os.path.abspath('./frontend')
static_dir = os.path.abspath('./frontend')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)


@app.route('/')
def hello():
   return render_template("index.html") 

#@app.route('/parse', methods=['POST'])
#def parser():
#    data = request.stream.read().decode()
#    return jsonify(main_parser.parse(data.splitlines()))

if __name__ == '__main__':
    app.run(host="0.0.0.0")
