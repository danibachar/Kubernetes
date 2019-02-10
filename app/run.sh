#!/bin/sh

exec gunicorn --config ./microservices/img/gunicorn-config.py --log-config ./microservices/img/logging.conf app:app
