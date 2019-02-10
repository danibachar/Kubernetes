#!/bin/bash

# Based - https://www.youtube.com/watch?v=JNnmgTjzo6A
#         https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/

###############################
# INIT
minikube start --extra-config=controller-manager.horizontal-pod-autoscaler-use-rest-clients=true --v=5
eval $(minikube docker-env)
minikube addons enable metrics-server
# RUN
kubectl apply -f hpa.yaml
# MONITOR
watch kubectl get services,pods,hpa -o wide
# DEBUGGING
minikube dashboard
watch kubectl describe nodes -o wide
kubectl describe nodes | grep -A 2 -e "^\\s*CPU Requests"
kubectl describe hpa hpa-example-autoscaler # Details on the autoscale
kubectl describe service hpa-example-svc
#TEST
# Single
curl http://$(minikube ip):31001/2 # make sure getting back Hey There response
curl http://$(minikube ip):31001/3 # Load
# Multi Load
kubectl run -i --tty load-generator --image=busybox /bin/sh
while true; do curl -s http://$(minikube ip):31001/3 ; done
#REMOVE
kubectl delete -f hpa.yaml
kubectl delete deployment load-generator
# Stop minikube - not mandatory
minikube stop
