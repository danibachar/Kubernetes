# Installation

## 1) GCP Attcker Machine config (TODO - dockerise)
    ### a) Allow full access for gcp api for the machine ( you know that tick you need to set when the machine is off...)
    ### b) Make sure `gcloud` is configured, on gcp machines it should come built-in.
    ### c) On local machine install gcloud and run gcloud auth login - login using you gcp account

## 2) install prerequsitis (ubuntu)

#### update
sudo apt-get update

#### CURL
sudo apt-get install -y curl

#### Java
sudo apt-get install -y default-jre openjdk-11-jre-headless openjdk-8-jre-headless

#### Node
curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
sudo apt install nodejs

#### Kubernetes - https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl-on-linux
sudo apt-get update && sudo apt-get install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl

#### Python
sudo apt-get install -y python3-pip

#### Some more dependencies
sudo npm install -g loadtest

## 4) Run - gcloud container clusters get-credentials microsvc-us --zone=us-central1-a

## 5) Make sure we got the api toke by running - cat ~/.kube/config
You should see some certificate or a Bearer token
You should see a context similar to this
```
 context:
    cluster: gke_independent-bay-250811_us-central1-a_microsvc-us
    user: gke_independent-bay-250811_us-central1-a_microsvc-us
  name: gke_independent-bay-250811_us-central1-a_microsvc-us
current-context: gke_independent-bay-250811_us-central1-a_microsvc-us
```

## 6) Remember to update the jmeter test cases with the new external ip address
Clone the repo, ammm  da....

## 7) now you should be able to run the script
``` Run the test
python3 yoyo_attaker_flow.py
optional live feed - python3 yoyo_attaker_flow.py &> live_feed.txt
```


### Helpers:
link - https://stackoverflow.com/questions/37333339/how-to-install-latest-jmeter-in-ubuntu-15-10
java --version

### JMeter
Jmeter is included under the yoyo_attcker directory - apache-jmeter-5.1.1

### Legacy

Other options for running load testing

1. Use locust
   1. Install - pip install -r requirements.txt
2. Use Vegeta
   1. Install - brew update && brew install vegeta
      https://github.com/tsenart/vegeta

``` Delete evicted pods
kubectl get pods | grep Evicted | awk '{print $1}' | xargs kubectl delete pod
```


```crontab
*/03 * * * nohup python3 -u /opt/Kubernetes/yoyo_attacker/yoyo_attaker_flow.py >> attacker.$(date +%Y-%m-%d_%H:%M).log 2>&1 &
```
