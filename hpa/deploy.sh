#!/bin/bash

gcloud container clusters get-credentials microsvc-us --zone=us-central1-a
# gcloud endpoints services deploy swagger.yaml

kubectl apply -f ingress.yaml
kubectl apply -f esp-nginx.yaml
kubectl apply -f hpa.yaml