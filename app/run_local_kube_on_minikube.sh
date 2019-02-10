#!/bin/bash

echo Init Local Development Environment...

minikube start
#This is a must to forward commands to the new minikube env
eval $(minikube docker-env)
minikube ip #to get local env ip

echo Finished Init minikube.

echo Deploying kubernetes

kubectl delete -f kube/local/minikube/deployment.yaml
make build-local-dev
kubectl apply -f kube/local/minikube/deployment.yaml
kubectl get po

# kubectl exec -i -t app-microsvc-488497908-cbmvq bash

# Optional to open access from your machine to the pod - port forwarding

#kubectl port-forward pod_name 8081
