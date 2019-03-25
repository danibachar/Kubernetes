``` Delete evicted pods
kubectl get pods | grep Evicted | awk '{print $1}' | xargs kubectl delete pod
```

``` Install the load test
npm install -g loadtest
```

``` Run the test
python yoyo_attaker_flow.py
```

```crontab
*/03 * * * nohup python3 -u /opt/Kubernetes/yoyo_attacker/yoyo_attaker_flow.py >> attacker.$(date +%Y-%m-%d_%H:%M).log 2>&1 &
```


Other options for running load testing

1. Use locust
   1. Install - pip install -r requirements.txt
2. Use Vegeta
   1. Install - brew update && brew install vegeta
      https://github.com/tsenart/vegeta
