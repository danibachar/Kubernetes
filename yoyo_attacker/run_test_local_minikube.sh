#!/bin/bash

# GOOD Documentation online
# _

locust -f ./yoyo.py --host=http://$(minikube ip):31001
http://35.192.24.244:31001