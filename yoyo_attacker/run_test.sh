#!/bin/bash

# GOOD Documentation online
# https://docs.locust.io/en/latest/quickstart.html

locust -f ./yoyo.py --host=http://$(minikube ip):31001