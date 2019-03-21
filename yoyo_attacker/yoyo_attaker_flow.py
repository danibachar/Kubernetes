from ratelimit import limits, sleep_and_retry
import requests
import datetime
import os
import subprocess
import sys
import csv
from kubernetes import client, config
from multiprocessing import Pool
from statistics import mean
import math
from threading import Timer
import numpy as np

dir_path = os.path.dirname(os.path.realpath(__file__))
csv_file_name = str(dir_path)+"/{}.table.csv".format(str(datetime.datetime.now()))

def safe_open(file_name_with_dierctory:str, permision="wb+"):
	if not os.path.exists(os.path.dirname(file_name_with_dierctory)):
	    try:
	        os.makedirs(os.path.dirname(file_name_with_dierctory))
	    except OSError as exc: # Guard against race condition
	        if exc.errno != errno.EEXIST:
	            raise

	return open(file_name_with_dierctory, permision)


# GLOBALS
END_POINT = 'http://130.211.200.247:31001/service'
CONFIG = {
    'scaled_attack': False, # A new options - aas noticed in experiments
    'r': 0, # Average requests rate per unit time of legitimate clients
    'k': 3, # power of attack
    'n': 0, # Number of attack cycles - Should be dynamic counter every on attack
    't': 0, # Cycle duration in seconds
    't_on': 80, # int, Time of on-attack phase in seconds, should be dynamic - we should be dynamic by the is_running_attack flag
    't_off': 0,# int, Time of off-attack phase in seconds - count dynamically
    'i_up': 0, # int, Threshold interval for scale-up in seconds. - NOT CONTROLED IN KUBERNETES
    'i_down': 0, # int, Threshold interval for scale-down in seconds. - NOT CONTROLED IN KUBERNETES
    'w_up': 0 #
}

# Probe packet
@sleep_and_retry
@limits(calls=1, period=1)
def send_probe(url):
    response = requests.get(url)
    if response.status_code != 200:
        res_time = 5
    else:
        res_time = response.elapsed.total_seconds()
    return res_time


def start_on_attack_phase():
    CONFIG['n']+=1
    rps = str(CONFIG['k'])
    p = subprocess.Popen(['loadtest', END_POINT, '-t', '1000', '-c', rps, '--rps', rps],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p

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
    def authenticate():
        config.load_kube_config(config_file='/home/danibacharfreegcp/.kube/config')
        client.configuration.api_key = {
            "authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tYmxtd2wiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6Ijg3NDAzMWI1LTQ3ZjktMTFlOS1iMDcwLTQyMDEwYTgwMDE2ZiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.BGn9dM2B2SJ8Ixkc8sS6v2oyP9xVM5dX57pJsyzYnOWqQtsIxisjqj5uq8k1sxhA0qEVyjFU11FLe4wDki2jxvxejcOo56MeN5wv7PeT_JAAQVso9ifFPDCtaBH-4gvJGbB8ukqADktOa9JXGFO5srYIKiCtsrOAgRbVYJLIzNruxbp84PqMp6U41lCqmu_xQ8QDyFetz-UKtN1hgOMj7gAmjInqEsSEaFlTesW5gk5WSwnICM8rAC0iOBF0ayQYB9yIoMnH-W2c3cfwDGqcXfm3jhuLz2vwPd9BlpaGk_KvN4vcKbLUUCCqJKml15-HgWMwHru-6jY8ADbngf6Qpg"}
        auto_scale_api = client.AutoscalingV1Api()
        cluster_api = client.CoreV1Api()
        return auto_scale_api, cluster_api
    # except Exception as e:
    #     print('error')


    autoscale_api_instance, cluster_api = authenticate()

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
    nodes_count = 6
    desire_pod_count = 6
    cpu_load = 0
    last_scale_time = None

    with safe_open(csv_file_name, 'w') as f:
        w = csv.writer(f, delimiter=',')
        # Probe test
        for index in range(5000):
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
                print('95th res time under attack  = {}'.format(per95_attack_res_time))
                print('90th res time under attack  = {}'.format(per90_attack_res_time))
                if index > 120 and cpu_load < 40 and current_pods_coount > 6:
                    is_running_attack = False
                    if attack_process:
                        try:
                            print("killing attack process - {}".format(attack_process))
                            attack_process.kill()
                            attack_process = None
                        except Exception as e:
                            print("kill attack fail - {}".format(e))


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
                if index == 50:  # first attack!
                    is_running_attack = True
                    print('init first attack')
                    latest_attack_index = index
                    attack_process = start_on_attack_phase()
                # latest_attack_index
                # We need to send a small burst of an attack and check for res_time > 2
                # This is a hack - please use prob above- just need to parse the output of the stdout
                if current_pods_coount == 6 and index > 50:
                    is_running_attack = True
                    latest_attack_index = index
                    print('init attack by POD COUNT on index = {}'.format(index))
                    attack_process = start_on_attack_phase()


            # Checking HPA every 60 sec
            if index % 10 == 0:
                name = 'hpa-example-autoscaler'
                namespace = 'default'
                try:
                    api_response = autoscale_api_instance.read_namespaced_horizontal_pod_autoscaler(name, namespace, pretty=True)
                    nodes_count = len(list(cluster_api.list_node().items))
                except Exception as e:
                    # TODO  -re authenticate
                    print('error trying to authenticate - {}'.format(e))
                    p = subprocess.Popen(['kubectl', 'get', 'hpa'],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print('BEFPRE p wait')
                    p.wait()
                    print('ACFTER p wait')
                    autoscale_api_instance, cluster_api = authenticate()
                    api_response = autoscale_api_instance.read_namespaced_horizontal_pod_autoscaler(name, namespace, pretty=True)
                    nodes_count = len(list(cluster_api.list_node().items))

                status = api_response.status
                current_pods_coount = status.current_replicas
                desire_pod_count = status.desired_replicas
                cpu_load = status.current_cpu_utilization_percentage
                last_scale_time = status.last_scale_time

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
                    'node_count',
                    'current_power_off_attack',
                    #
                    'is running attach',
                    #
                    'last_scale_time',

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
                cpu_load/-100, # Normelize
                nodes_count,
                (CONFIG['k'] + CONFIG['n']),
                # is
                int(is_running_attack)*(-5), # Nonmalize
                #
                last_scale_time
                ])
    print('config - {}'.format(CONFIG))


start()
