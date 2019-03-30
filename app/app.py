# -*- coding: utf-8 -*-

import os
import sys
# Hack to alter sys path, so we will run from microservices package
# This hack will require us to import with absolut path from everywhere in this module
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(APP_ROOT))

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return 'OK'

@app.route('service/<power>', methods=['GET'])
def default_get(power):
    y = 2**2**2**2**2
    for _ in range(10*int(power)):
        pass
    return 'Hey There! {}'.format(y)


if __name__ == '__main__':
    # threaded=True is a debugging feature, use WSGI for production!
    app.run(host='0.0.0.0', port='8081', threaded=True)
