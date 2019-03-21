``` Delete evicted pods
kubectl get pods | grep Evicted | awk '{print $1}' | xargs kubectl delete pod
```

``` Install the load test
npm install -g loadtest
```

``` Run the test
python yoyo_attaker_flow.py
```


Other options for running load testing

1. Use locust
   1. Install - pip install -r requirements.txt
2. Use Vegeta
   1. Install - brew update && brew install vegeta
      https://github.com/tsenart/vegeta
