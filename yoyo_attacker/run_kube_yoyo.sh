export SERVICE_HOST_ENV_NAME=''
export GOOGLE_APPLICATION_CREDENTIALS='/Users/danielbachar/Documents/IDC/Kubernetes/yoyo_attacker/woven-phoenix-234610-96536085aad9.json'



REMOVE ME

project_id = 'woven-phoenix-234610'
cluster_id = 'yoyo-attack'
zone = 'us-central1-a'

import googleapiclient.discovery

service = googleapiclient.discovery.build('container', 'v1')
clusters_resource = service.projects().zones().clusters()

clusters_response = clusters_resource.list(projectId=project_id, zone=zone).execute()


res = service.projects().zones().clusters().get(projectId='woven-phoenix-234610', zone='us-central1-a', clusterId='yoyo-attack').execute()

res = service.projects().zones().clusters().nodePools().list(projectId='woven-phoenix-234610', zone='us-central1-a', clusterId='yoyo-attack').execute()
res = service.projects().zones().clusters().nodePools().get(projectId='woven-phoenix-234610', zone='us-central1-a', clusterId='yoyo-attack',nodePoolId='default-pool').execute()


res = service.projects().zones().operations()


from google.auth import compute_engine
from google.cloud.container_v1 import ClusterManagerClient
from kubernetes import client

credentials = compute_engine.Credentials()
cluster_manager_client = ClusterManagerClient(credentials=credentials)
cluer = cluster_manager_client.get_cluster(project_id, zone, cluster_id)
configuration = client.Configuration()
configuration.host = f"https://{cluster.endpoint}:443"
configuration.verify_ssl = False
configuration.api_key = {"authorization": "Bearer " + credentials.token}
client.Configuration.set_default(configuration)
v1 = client.CoreV1Api()
print("Listing pods with their IPs:")
pods = v1.list_pod_for_all_namespaces(watch=False)
for i in pods.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))