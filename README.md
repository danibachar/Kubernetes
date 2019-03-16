# Kubernetes
Repo With base installation and guidelines on installing and deploying basic kubernetes cluster on minnikube and GCP

Coding Style
------------
### Python
We've made an effort to adhere to proper Python coding style:

* PEP 8 -- [Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
* PEP 257 -- [Docstring Conventions](https://www.python.org/dev/peps/pep-0257)
* PEP 484 -- [Type Hints](https://www.python.org/dev/peps/pep-0484/#suggested-syntax-for-python-2-7-and-straddling-code)


Setting Up A Local Development Environment
------------------------------------------
In order to hit the ground running we recommend using [minikube](https://github.com/kubernetes/minikube), which is a
development tool that runs Kubernetes locally. Throughout this section we assume that you have the
[Google Cloud SDK](https://cloud.google.com/sdk/downloads) installed properly, namely the `gcloud` CLI, as well as
the `kubectl` component. `kubectl` must be properly configured to work with your local `minikube` installation.

### Install Minikube
Here's what you should do to get started and verify your minikube environment.

* Install the latest version of the [Docker Engine](https://docs.docker.com/engine/installation/).
* Install [Google Cloud SDK](https://cloud.google.com/sdk/downloads) (`gcloud`) including the `kubectl` component
* Install [minikube](https://github.com/kubernetes/minikube)
* Start minikube by running `minikube start`, to start with certain disk space `minikube start --disk-size 50g`
* Make sure the local minikube cluster is up by running `kubectl cluster-info`
* Point your Docker environment to minikube by running `eval $(minikube docker-env)`

## Minikube Know Issues
* https://github.com/kubernetes/minikube/issues/497

## Kubectl CLI - Usefull commands - Updated to version 145 (March 2017)
## link - https://kubernetes.io/docs/user-guide/kubectl-overview/
* "kubectl get pod -a" - list pods
* "kubectl get jobs" - get jobs list
* "kubectl describe pod + pod_name" - describe the pod
* "kubectl describe job + job_name" - describe job
* "kubectl apply -f name.yaml" - runs the kubernetis cluster, if we have a problem we need to remove it
* "kubectl delete -f name.yaml" - to delete the former cluster we deployed
* "kubectl delete pods + pod_name" - to delete certain pod
* "kubectl apply -f job-test.yaml" - To Run Tests
* "kubectl delete -f job-test.yaml" - To Delete Tests
* "kubectl exec pod_name -i -t -- bash" - to access the pod bash
* "kubectl port-forward pod_name source_port:dest_port" - to forward port 27017 to the relevant  pod
* "kubectl logs + pod_name + (container if there is more than one container in pod)“
   show us the log of the pod, if the pod holds more than one container we need to list them
Practical Examples - for dev/prod environments:
* kubectl logs --namespace=dev search-microsvc-996702333-6jjkx search-microsvc-cont
* kubectl logs --namespace=dev img-srv-1888727084-4ms5q img-microsvc-cont
* kubectl logs --namespace=dev img-srv-2289938334-4dt7d img-microsvc-nginx
* kubectl exec -i -t img-1888727084-4ms5q -c img-cont bash --namespace=dev
* kubectl exec -i -t img-1888727084-4ms5q -c img-nginx bash --namespace=dev
* kubectl logs --namespace=dev img-redis-3939525175-9w7xp
* kubectl describe --namespace=dev pod img-3730747389-r829f

## Kubectl Remove node process
This is a list of potential execution steps:

Mark current node as unshedulable aka cordon the node
Drain the node
Restart the kubelet with empty or default values, e.g. crash-loop until an API server is provided
1 - Existing kubectl code living in pkg/kubectl/cmd/drain.go should be either re-used or adapted.
2 - kubeadm reset should execute similarly, differing only in the last step where instead of restarting, it should stop the kubelet.

Thoughts?

## Docker CLI  - Usefull commands - Updated to version 145 (March 2017)
* "docker images" - lists docker images
* "docker-machine --create" - create local docker machine
* "docker build -t search:test -f Dockerfile.test ../../" - build our wanted docker image that later we are going to
* "docker rmi `docker images --filter 'dangling=true' -q --no-trunc`" - this removes all the dangling non intermediate <none> images:
* "docker rm `docker ps -aq --no-trunc --filter "status=exited"`" -  removing all containers that are not running:
* "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock:ro -v /var/lib/docker:/var/lib/docker martin/docker-cleanup-volumes" - volume cleanup when no disk space left

** To Build Docker image look into the Make file to see which builds are avialable
** You will need to re-build your docker image, and re-deploy for each change in the code (at list until we configure a better development env)


Setting Up The GKE Cluster From Scratch
---------------------------------------
__Note:__ This is only necessary when setting up a new cluster in the cloud.

Throughout this section we assume that you have the [Google Cloud SDK](https://cloud.google.com/sdk/downloads) installed
properly, namely the `gcloud` CLI, as well as the `kubectl` component.
`gcloud` should be properly configured to work with your GCP project
(e.g. `batcat-1306`, which we will use).

### Deploying the API
Before we can use our API we need to deploy the API definition to Google Cloud
Endpoints, which provides monitoring, logging, security and so on. The domain
name needs to be verified by Google before deployment. To deploy the API, run:

Dev:

`gcloud endpoints services deploy swagger_dev.yaml`

Prod:

`gcloud endpoints services deploy swagger_prod.yaml`

__Note:__ Google Cloud Endpoints is still in beta and subject to unexpected
changes from time to time.

Make note of the API service name and revision, we will need it later to
configure the ESP. Also, make sure you've generated appropriate API keys through
GCP's API Manager, otherwise some endpoints may not be accessible.

### Creating the cluster
The following command creates a new GKE cluster spanning across four zones for
high availability. The initial node pool has four `n1-standard-1` nodes (one
node in each zone).

Asia - `gcloud container clusters create "your_cluster_name" --zone "asia-northeast1-a" --machine-type "n1-standard-1" --num-nodes "1"`

If you want to enable cluster autoscaling
gcloud container clusters create "yoyo-attack" \
--zone us-central1-a \
--machine-type "n1-standard-1" \
--num-nodes 5 --enable-autoscaling --min-nodes 6 --max-nodes 15 \
--metadata disable-legacy-endpoints=true

gcloud container clusters update yoyo-attack --zone us-central1-a --enable-autoscaling --min-nodes 4 --max-nodes 10

The cost of this humble cluster is approximately $101/mo. Once the cluster is up
and running there will probably be no need to ever tear it down, as long as it
serves production traffic, otherwise downtime will occur and that's a boo-boo.
The cluster's capacity may be scaled up/down by:

* Changing the number of nodes and/or the number of zones.
* Changing node machine types - multiple node pools may be used to allow
  different machine types.
* Future: Adding/removing additional GCP regions (currently unsupported by GKE).

Once the cluster is ready, pull its credentials by running:
Prod:

`gcloud container clusters get-credentials your_cluster_name --zone=asia-northeast1-a`

project_id = 'woven-phoenix-234610'
cluster_id = 'yoyo-attack'
zone = 'us-central1-a'

gcloud config set project woven-phoenix-234610
gcloud container clusters get-credentials yoyo-attack --zone=us-central1-a

This will point `kubectl` to work with our cluster. Currently, _dev_ and _prod_
environments are deployed on the same cluster for operational convenience, but
they will be completely separated by Kubernetes namespaces so they are unable to
access each other's resources. Define the namespaces in which we will operate:

Dev: `kubectl create namespace dev`

To avoid specifying `--namespace=dev` in every command, we can use
`kubectl config set-context <CONTEXT-NAME> --namespace=<dev/prod>`
to set the proper context persistently.

### Creating the configuration

#### ConfigMaps
ConfigMap resources are key-value stores which we use to hold all non-sensitive
environment configuration. All microservices depend on them and may not be able
to initialize properly before they are created.
We have a few different ConfigMaps for different purposes:

* config - General Application/Microservice configuration. Config values are
  injected into the pods as environment variables.
* hosts - An addition to `/etc/hosts` used as a hack to resolve hostnames in
  AWS. Hopefully we can get rid of this once we fully migrate to GCP. This
  ConfigMap is mounted as a volume to the filesystem.
* nginx.conf - General nginx configuration for the ESP containers (which are
  nginx based). This is needed to enable Cloud Endpoints integration, respond to
  health checks properly, enable gzip compression, etc. This ConfigMap is
  mounted as a volume to the filesystem.

Create ConfigMaps by running:

Prod:

`kubectl create -f ./<microsvc_name>/kube/prod/config.yaml
Example - kubectl create -f ./translate/kube/prod/config.yaml

`kubectl create -f ./config/esp-nginx-prod.yaml`

### Handling incoming traffic
An Ingress is a collection of traffic routing rules that allow inbound traffic
to reach the microservices within our cluster. It is operated by an Ingress
Controller (GLBC) pod which is deployed inside every GKE cluster by default. The
GLBC uses a Google Compute Engine L7 Load Balancer to route the traffic.

__Note:__ Ingress is a beta resource.

#### Reserve static IP addresses
Public static IPs can be reserved for use by the Ingress, so that we may use
them in our DNS records:

Prod:

`gcloud compute addresses create api-prod --global`

#### Create the Ingress
Once the Ingress is created it takes care of setting up the load balancer,
backend services, url maps, forwarding rules, firewall rules and other GCE
resources needed for it to function. See the References section for more
information.

Dev:
create - `kubectl create -f ./ingress/ingress-dev.yaml`
update - `kubectl apply -f ./ingress/ingress-dev.yaml`
To check that ingress was deployed correctly run:
`kubectl get ing --namespace=dev`

Prod:
create - `kubectl create -f ./ingress/ingress-prod.yaml`
update - `kubectl apply -f ./ingress/ingress-prod.yaml`
To check that ingress was deployed correctly run:
`kubectl get ing --namespace=prod`

It normally takes up to 5 minutes until everything is up and running.


### Set up the Microservices
Each microservice should be self-contained and able to be deployed and scaled
independently of other microservices. The microservice's entry point is a
service which allows it to be discovered and used by other microservices and
inbound traffic routed by the ingress.

#### Build and Deployment Process
__NOTE__: This is a work in progress.
Each Microservice supplies a Makefile for building its container and deploying
it to the cluster. Deployment can be either from scratch or as a rolling update
to an existing deployment and is handled by Kubernetes. Microservice deployments
and containers should be labelled and tagged properly so that we can easily
identify locate their source code within the Git repository and to allow
rollback. _Bad_ version tags would be, for example: "latest", "v1",
"2016-11-17", etc. For more details, see the Makefile.

The supported `make` commands are:

`make build` - Builds and pushes a Docker container that holds the microservice.

`make deploy-(dev/prod)` - Builds the container and then deploys it to the cluster
according to the deployment configuration.

General Microservice Structure
------------------------------
Each Microservice roughly follows this template:

* A microservice is a deployment which manages an underlying replica set of
  pods. The number of pods may be scaled independently of other microservices.
* Each pod holds two containers: ESP (Extensible Service Proxy) supplied by
  Google for integration with Cloud Endpoints, and the actual microservice pod.
  The ESP pod is powered by nginx and directs incoming traffic to the
  microservice container which is not directly exposed. At the moment,
  microservice pods are powered by Flask+Gunicorn, but future microservices may
  use any framework, as long as it serves RESTful APIs over HTTP. Moreover,
  future microservices may define additional containers and pods they require to
  function properly.
* Each group of pods is labelled as an app (e.g.: `app: search-microsvc`)
  and the label serves as a selector for a wrapper service that allows auto
  discovery and load balancing for the microservice within the cluster.
