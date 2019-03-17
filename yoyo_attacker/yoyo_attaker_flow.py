



# installations - pip install --upgrade google-api-python-client
#

# Must export env var for authentication


import argparse
import googleapiclient.discovery

def list_clusters_and_nodepools(project_id='woven-phoenix-234610', zone='us-central1-a'):
    """Lists all clusters and associated node pools."""
    service = googleapiclient.discovery.build('container', 'v1')
    clusters_resource = service.projects().zones().clusters()

    clusters_response = clusters_resource.list(projectId='woven-phoenix-234610', zone='us-central1-a').execute()

    for cluster in clusters_response.get('clusters', []):
        print("Cluseter - Nodes - {}".format(cluster.get('currentNodeCount',None)))
        print("Cluster Status - {}".format(cluster.get('status',None)))
#
#
# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(
#         description=__doc__,
#         formatter_class=argparse.RawDescriptionHelpFormatter)
#     subparsers = parser.add_subparsers(dest='command')
#     list_clusters_and_nodepools_parser = subparsers.add_parser(
#         'list_clusters_and_nodepools',
#         help=list_clusters_and_nodepools.__doc__)
#     list_clusters_and_nodepools_parser.add_argument('project_id')
#     list_clusters_and_nodepools_parser.add_argument('zone')
#
#     args = parser.parse_args()
#
#     if args.command == 'list_clusters_and_nodepools':
#         list_clusters_and_nodepools(args.project_id, args.zone)
#     else:
#         parser.print_help()



# TODO -
# 1) get info about:
#   a) cluseter size - number of nodes
#   b) nodes - requested and allocated cpu
#   c) number of pods in each node
#   d) hpa - target and actuall cpu consumption
#   e) request time
#   f) RPM(S) - requests per minute (second)
#
# 2) Flow
#   a) regular traffic:
#       5 RPM
#       1 pod
#       cluster size - 3 nodes
#   b) yoyo attack - bursts of requests
#       power of attack = k
#
# Attack input
#

from ratelimit import limits, sleep_and_retry
import requests
import datetime
import os
import subprocess
import sys
import csv
from kubernetes import client, config
import googleapiclient.discovery
from multiprocessing import Pool
from statistics import mean
import math
from threading import Timer
import numpy as np


# config = {
#     'power_of_attack': 2,
#
# }


response_times = []
timeline = []
dir_path = os.path.dirname(os.path.realpath(__file__))
csv_file_name = str(dir_path)+"/{}.table.csv".format(str(datetime.datetime.now()))

@sleep_and_retry
@limits(calls=30, period=60)
def call_api(url):
    response = requests.get(url)

    if response.status_code != 200:
        res_time = -1
    else:
        res_time = response.elapsed.total_seconds()
    return  res_time


def safe_open(file_name_with_dierctory:str, permision="wb+"):
	if not os.path.exists(os.path.dirname(file_name_with_dierctory)):
	    try:
	        os.makedirs(os.path.dirname(file_name_with_dierctory))
	    except OSError as exc: # Guard against race condition
	        if exc.errno != errno.EEXIST:
	            raise

	return open(file_name_with_dierctory, permision)

def send_probe():
    # TODO - send probe packet to diccover when scale up is done?
    return


def start_yoyo_attack(k=1, n=1, t=120, t_on=120, t_off=120, i_up=120, i_down=120, w_up=120, w_down=120):
    """ Regular working with the server

     Construct a Resource object for interacting with an API. The serviceName and
     version are the names from the Discovery service.

     Args:
       k: int, power of attack
       n: int, Number of attack cycles
       t: int, Cycle duration in seconds
       t_on: int, Time of on-attack phase in seconds
       t_off: int, Time of off-attack phase in seconds
       i_up: int, Threshold interval for scale-up in seconds.
       i_down: int, Threshold interval for scale-down in seconds.
       w_up: int, Threshold interval for scale-up in seconds.
       w_down: int, Threshold interval for scale-up in seconds.

     Returns:
       File name with the statistics on the attack
     """
    with safe_open(csv_file_name, 'w') as f:
        w = csv.writer(f, delimiter=',')
        # w.writeheader()
        for _ in range(300):
            res_time = call_api("http://35.239.69.254:31001/service")
            curr_time = str(datetime.datetime.now())
            print("res time in seconds - {}".format(res_time))
            response_times.append(str(res_time))
            timeline.append(curr_time)

            if w:
                w.writerow([curr_time, str(res_time)])


# def start_server_regular_traffic():

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(
#         description=__doc__,
#         formatter_class=argparse.RawDescriptionHelpFormatter)
#     subparsers = parser.add_subparsers(dest='command')
#     list_clusters_and_nodepools_parser = subparsers.add_parser(
#         'list_clusters_and_nodepools',
#         help=list_clusters_and_nodepools.__doc__)
#     list_clusters_and_nodepools_parser.add_argument('project_id')
#     list_clusters_and_nodepools_parser.add_argument('zone')
#
#     args = parser.parse_args()
#
#     if args.command == 'list_clusters_and_nodepools':
#         list_clusters_and_nodepools(args.project_id, args.zone)
#     else:
#         parser.print_help()

# GLOBALS
END_POINT = 'http://130.211.200.247:31001/service'
CONFIG = {
    'scaled_attack': False, # A new options - aas noticed in experiments
    'r': 0, # Average requests rate per unit time of legitimate clients
    'k': 4, # power of attack
    'n': 0, # Number of attack cycles - Should be dynamic counter every on attack
    't': 0, # Cycle duration in seconds
    't_on': 80, # int, Time of on-attack phase in seconds, should be dynamic - we should be dynamic by the is_running_attack flag
    't_off': 0,# int, Time of off-attack phase in seconds - count dynamically
    'i_up': 0, # int, Threshold interval for scale-up in seconds. - NOT CONTROLED IN KUBERNETES
    'i_down': 0, # int, Threshold interval for scale-down in seconds. - NOT CONTROLED IN KUBERNETES
    'w_up': 0 #
    # SCALE_DOWN_TEST_CONFIG: {
    #
    # }

}

""" Regular working with the server

 Construct a Resource object for interacting with an API. The serviceName and
 version are the names from the Discovery service.

 Args:
   k: int, power of attack
   n: int, Number of attack cycles
   t: int, Cycle duration in seconds
   t_on: int, Time of on-attack phase in seconds
   t_off: int, Time of off-attack phase in seconds
   
   i_up: int, Threshold interval for scale-up in seconds.
   i_down: int, Threshold interval for scale-down in seconds.
   w_up: int, Threshold interval for scale-up in seconds.
   w_down: int, Threshold interval for scale-up in seconds.

 Returns:
   File name with the statistics on the attack
 """
class Attacker(object):
    """docstring for Tester."""

    def __init__(self, args):
        super(Attacker, self).__init__()
        self.k = args.get('k', 1)
        self.n = args.get('n', 1)
        self.t = 0
        self.t_on = args.get('t_on', 100)
        self.t_off = args.get('t_off', 330)

        self.i_up = 0 # None
        self.i_down = 0  # None
        self.w_up = 0  # None
        self.w_down = 0  # None

        self.is_attack_on = False

    # Probe packet
    def start_attack(self):
        p = subprocess.Popen(['loadtest', END_POINT, '-t', str(self.t_on), '-c', str(self.k), '--rps', str(self.k)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.is_attack_on = True
        print('ATTACK IS ON')

    def start(self):
        pass

# Probe packet
@sleep_and_retry
@limits(calls=1, period=1)
def send_probe(url):
    response = requests.get(url)

    if response.status_code != 200:
        res_time = 5
        print('500 error')
    else:
        res_time = response.elapsed.total_seconds()
    return res_time

def start_on_attack_phase():
    CONFIG['n']+=1
    rps = str(CONFIG['k'])
    p = subprocess.Popen(['loadtest', END_POINT, '-t', '230', '-c', rps, '--rps', rps],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p
    # print(p.stderr)
    # print(p.stdout)

def scale_down_is_over_test():
    p = subprocess.Popen(['loadtest', END_POINT, '-t', '5', '-c', '10', '--rps', '10'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = list(iter(p.stdout.readline, b''))
    output = str(lines[-1]).split(' ')
    ms_index = output.index('ms')
    res = float(output[ms_index-1]) / 1000
    # print('scale prob longest time {}'.format(res))/
    print('scale prob longest time {}'.format(res))
    # for line in iter(p.stdout.readline, b''):
    #     print(line)
    return math.floor(res) >= 2


def start():
    """
    Attack Flow:
    Our humble cluster contains 5 nodes, aorund 1 node is dedicated for Kubernetes internal services 
    (pods which might spread ammoung different nodes)
    And with a minimum of 2 pods to be able to hold some load
    
    Nodes hold 1 or more pods
    Pod holds 1 or more containers (Apps) in our case each pod equals 1 app server
    
    Each pod is configured to consume 200m CPU out of the 1 CPU each node is get    
    
    We configure the experiment time as 5 minutes (300 seconds) 
    Which we will send a stead stream of 1 probe packet to follow the response time each 5 seconds
    This `Steady State` consumes 25% of the resources we have in the cluster 
    (remember at that state we only ahve 2 pods running
    
    
    The attack kiks in after 150 cycles and produces 1 RPS for 1 minute 
    
    GKE the control plane is not accessible, which means we cannot control the scale/cool down delay threshold 
     
    We
    """
    # api_instance = None
    # try:
    config.load_kube_config()
    api_instance = client.AutoscalingV1Api()
    # except Exception as e:
    #     print('error')



    probe_time_tupples = []
    is_running_attack = False
    probs_times_under_attack = []
    latest_attack_index = 0
    attack_process = None
    mean_attack_res_time = 0
    avg_attack_res_time = 0
    per90_attack_res_time = 0
    per95_attack_res_time = 0

    current_pods_coount = 6
    desire_pod_count = 6
    cpu_load = 0
    last_scale_time = None
    print(csv_file_name)
    with safe_open(csv_file_name, 'w') as f:
        w = csv.writer(f, delimiter=',')
        # Probe test
        for index in range(1500):
            res_time = send_probe(END_POINT)
            # Checking
            if is_running_attack:
                # Handle attack testing on cool down
                print('We Are under attack - checking!')
                # calc avg time
                probs_times_under_attack.append(res_time)
                sample_count = len(probs_times_under_attack)
                mean_attack_res_time = mean(probs_times_under_attack)
                avg_attack_res_time = sum(probs_times_under_attack) / sample_count
                per95_attack_res_time = np.percentile(np.array(probs_times_under_attack), 95)
                per90_attack_res_time = np.percentile(np.array(probs_times_under_attack), 90)
                print('avg res time under attack  = {}'.format(avg_attack_res_time))
                print('mean res time under attack  = {}'.format(mean_attack_res_time))

                # if mean_res_time and float(mean_res_time) < 4:
                #     is_running_attack = False
                #     if attack_process:
                #         try:
                #             print("killing attack process - {}".format(attack_process))
                #             attack_process.kill()
                #         except Exception as e:
                #             print("kill attack fail - {}".format(e))
                #     print('Probe for scale Up finished (probably)')


                if latest_attack_index + 200 <= index:
                    is_running_attack = False
                    if attack_process:
                        try:
                            print("killing attack process - {}".format(attack_process))
                            attack_process.kill()
                            attack_process = None
                        except Exception as e:
                            print("kill attack fail - {}".format(e))
                    print('Attack is over')

            else:
                # Resting avg
                avg_attack_res_time = 0
                mean_attack_res_time = 0
                per95_attack_res_time = 0
                per90_attack_res_time = 0
                probs_times_under_attack = []
                # Handle no in attack logic - should we init one?
                # Check pod number od res time
                print('We Are at peace checking if we should start the attack on titan!')
                print('Latest attack index - {}'.format(latest_attack_index))
                # if index % 120 == 0: # 360 = grace period for cool down to kik
                #     print('Burst test')
                #     can_attack_again = scale_down_is_over_test()
                #     if can_attack_again:
                #         print('can attack again scale_down_is_over_test')
                #         is_running_attack = True
                #         latest_attack_index = index
                #         print('init attack on index = {}'.format(index))
                #         attack_process = start_on_attack_phase()
                if index == 50:  # first attack!
                    is_running_attack = True
                    print('init first attack')
                    latest_attack_index = index
                    attack_process = start_on_attack_phase()
                # latest_attack_index
                # We need to send a small burst of an attack and check for res_time > 2
                # This is a hack - please use prob above- just need to parse the output of the stdout
                elif latest_attack_index + 500 < index:
                    is_running_attack = True
                    latest_attack_index = index
                    print('init attack on index = {}'.format(index))
                    attack_process = start_on_attack_phase()


            # Checking HPA every 60 sec
            if index % 20 == 0:
                # if api_instance == None:
                #     break
                name = 'hpa-example-autoscaler'
                namespace = 'default'
                api_response = api_instance.read_namespaced_horizontal_pod_autoscaler(name, namespace, pretty=True)
                status = api_response.status
                current_pods_coount = status.current_replicas
                desire_pod_count = status.desired_replicas
                cpu_load = status.current_cpu_utilization_percentage
                last_scale_time = status.last_scale_time
                print('{} , {} , {}, {}'.format(current_pods_coount,desire_pod_count,cpu_load,last_scale_time))
                # print('current pods count {}'.format(status))

            # Get avarage time of the last x res and see if attack
            probe_time_tupples.append(res_time)
            CONFIG['r'] = sum(probe_time_tupples) / len(probe_time_tupples)
            print("res time in seconds - {}, index = {}".format(res_time, index))
            if index == 0:
                # Add headers
                w.writerow([
                    'time',
                    'current response time',
                    # Under attack
                    'avg response time under attack',
                    'mean response time under attack',
                    '95th percentile under attack response time',
                    '90th percentile under attack response time',
                    # Total
                    'probe packet avg response time',
                    'probe packet mean response time',
                    'probe packet 95th percentile response time',
                    'probe packet 90th percentile response time',
                    # HPA info
                    'current_pods_coount',
                    'desire_pod_count',
                    'cpu_load',
                    'last_scale_time',
                    #
                    'is running attach',

                ])

            w.writerow([
                index, # time
                min(round(res_time, 1),5), # probe response time - flatten weird results
                # Attack
                avg_attack_res_time,
                mean_attack_res_time,
                per95_attack_res_time,
                per90_attack_res_time,
                # probe
                (sum(probe_time_tupples) / len(probe_time_tupples)), # total avg res time
                mean(probe_time_tupples),  # total mea res time
                np.percentile(np.array(probe_time_tupples),90),
                np.percentile(np.array(probe_time_tupples), 95),
                # HPA INFO
                current_pods_coount,
                desire_pod_count,
                cpu_load,
                last_scale_time,
                # is
                int(is_running_attack)*(-5) # is on attack flag

                ])
    print('config - {}'.format(CONFIG))
#loadtest http://35.226.116.34:31001/service -t 60 -c 10 --rps 4
# start_yoyo_attack()
start()

# from google.auth import compute_engine
# # from google.cloud.container_v1 import ClusterManagerClient
# from kubernetes import client, config
#
# project_id = 'woven-phoenix-234610'
# zone = 'us-central1-a'
# cluster_id = 'yoyo-attack'
#
# credentials = compute_engine.Credentials()
#
# # cluster_manager_client = ClusterManagerClient(credentials=credentials)
# # cluster = cluster_manager_client.get_cluster(project_id, zone, cluster_id)
# #
# configuration = client.Configuration()
# # configuration.host = f"https://{cluster.endpoint}:443"
# configuration.verify_ssl = False
# configuration.api_key = {"authorization": "Bearer " + credentials.token}
# client.Configuration.set_default(configuration)
#
# v1 = client.CoreV1Api()
# print("Listing pods with their IPs:")
# pods = v1.list_pod_for_all_namespaces(watch=False)
# for i in pods.items:
#     print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))