# -*- coding: utf-8 -*-

import os
import sys
import math
# Hack to alter sys path, so we will run from microservices package
# This hack will require us to import with absolut path from everywhere in this module
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(APP_ROOT))

from flask import Flask, request, jsonify, send_file, send_from_directory
from werkzeug.contrib.fixers import ProxyFix
from flask_cors import CORS

# create flask instance
app = Flask(__name__)
# Enable cross origin
CORS(app)

# health check for load balancer
@app.route('/health', methods=['GET'])
def health():
    return 'OK'

@app.route('/<power>', methods=['GET'])
def default_get(power):
    y = 2**2**2**2**2**2
    x = 2
    for _ in range(0,int(power)):
        x = x*10

    for i in range(0,x):
        v = math.sqrt(i)

    return 'Hey There!'


if __name__ == '__main__':
    # threaded=True is a debugging feature, use WSGI for production!
    app.run(host='0.0.0.0', port='8081', threaded=True)
