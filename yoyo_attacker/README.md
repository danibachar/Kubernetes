# We have 2 options for running load testing

# 1) Use locust
#    a) Install - pip install -r requirements.txt
# 2) Use Vegeta
#    a) Install - brew update && brew install vegeta
#       https://github.com/tsenart/vegeta

# DELETE Evicted pods
# kubectl get pods | grep Evicted | awk '{print $1}' | xargs kubectl delete pod
