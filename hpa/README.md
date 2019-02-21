
# Brief explanation on a quick setup of the testing environment


1) Create a GCP Account

2) Open GCP Console

3) Clone the Kubernetes Repo

l

4) Create a Kubernetes Cluster + Autoscale:
It is important to set the initail cluster size to be enough to test only the HPA mechanism

gcloud container clusters create "microsvc-us" \
--zone us-central1-a \
--machine-type "n1-standard-1" \
--num-nodes 3 --enable-autoscaling --min-nodes 3 --max-nodes 20 \
--metadata disable-legacy-endpoints=true

5) Build Image

5.1) first we need to get the credentials for the cluster
gcloud container clusters get-credentials microsvc-us --zone=us-central1-a

5.2) Second we need to build and push the container (Described in the Docker File)
# Make sure you update the Makefile with your own GCP Project

cd hpa
make build

6) Deploy Container

# If image is built once and had no changes in code/docker file no need to build, we can just deploy
# Make sure the image you build is the image described in the .yaml file ( in this specific case hpa.yaml)
cd hpa
make deploy

7) monitoring that all is ok

watch kubectl get pods,nodes,hpa,services

# Brief explanation on the kubestl output
7.1) pods - will show the application pods
7.2) nodes - will show the cluster nodes
7.3) hpa - will show the state of the Kubernetes Horizontal Pod Autoscale
7.4) services - will show the defferent services we created
7.4.1) LoadBalalcer - the external IP address to access
7.4.2) Cluster IP


