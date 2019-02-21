import csv
import datetime
import errno
import math
import os
import subprocess
import sys
from statistics import mean

import numpy as np
import requests
from kubernetes import client, config
from ratelimit import limits, sleep_and_retry

dir_path = os.path.dirname(os.path.realpath(__file__))
csv_file_name = str(dir_path) + "/{}.table.csv".format(str(datetime.datetime.now()))

# Helper Functions
def safe_open(file_name_with_dierctory: str, permision="wb+"):
    if not os.path.exists(os.path.dirname(file_name_with_dierctory)):
        try:
            os.makedirs(os.path.dirname(file_name_with_dierctory))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    return open(file_name_with_dierctory, permision)

def get_power_of_attack(attack_type):
    if attack_type == 1:
        return 3
    return 10

# GLOBALS
'''
    The Endpoint to attack!
'''
HOST = "http://35.188.13.155"
END_POINT = '{}:31001/service/1000'.format(HOST)
'''
    1 - Experiment 1, where we attack without trigger the Cluster Autoscaling
    2 - Experiment 2 - Naive
    3 - Experiment 2 - Sophisticated
'''
ATTACK_TYPE = 3
CONFIG = {
    'scaled_attack': True,  # A new options - aas noticed in experiments
    'r': 5,  # Average requests rate per unit time of legitimate clients
    'k': get_power_of_attack(ATTACK_TYPE),  # power of attack
    'n': 0,  # Number of attack cycles - Should be dynamic counter every on attack
    'T': 0,  # Cycle duration in seconds
    't_on': 0,
    # int, Time of on-attack phase in seconds, should be dynamic - we should be dynamic by the is_running_attack flag
    't_off': 0,  # int, Time of off-attack phase in seconds - count dynamically
    'i_up': 0,  # int, Threshold interval for scale-up in seconds. - NOT CONTROLED IN KUBERNETES
    'i_down': 0,  # int, Threshold interval for scale-down in seconds. - NOT CONTROLED IN KUBERNETES
    'w_up': 0 , #
    'ragular_load': 'jmeter_test_cases/yoyo/regulat_load.jmx',
    'attack_load': 'jmeter_test_cases/yoyo/attack_load.jmx',
}

def jmeter_command(test_case):
    JMETER = ["./apache-jmeter-5.1.1/bin/jmeter"]
    FLAGS = ['-n'] + ['-t {}'.format(test_case)]# + ['-l {}_res.csv'.format('test.test')]
    print(JMETER + FLAGS)
    return JMETER + FLAGS

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

# loadtest 'http://35.239.228.131:31001/service/10000' -t 1000 -c 4 --rps 4
def start_on_attack_phase():
    print('starting attack')
    CONFIG['n'] += 1
    rate = str(CONFIG['r'] * CONFIG['k'])
    if CONFIG.get('scaled_attack', False):
        rate = str(int(rate) + CONFIG['n'])

    # p = subprocess.Popen(['loadtest', END_POINT, '-t', '100000', '-c', rate, '--rps', rate],
    #                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    p = subprocess.Popen(jmeter_command(CONFIG['attack_load']), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p


def start_regular_load():
    print('starting regular load')
    r = str(CONFIG['r'])
    p = subprocess.Popen(jmeter_command(CONFIG['ragular_load']), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # p = subprocess.Popen(['loadtest', END_POINT, '-t', '100000', '-c', r, '--rps', r],
    #                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p


# def scale_down_is_over_test():
#     p = subprocess.Popen(['loadtest', END_POINT, '-t', '5', '-c', '10', '--rps', '10'],
#                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     lines = list(iter(p.stdout.readline, b''))
#     output = str(lines[-1]).split(' ')
#     ms_index = output.index('ms')
#     res = float(output[ms_index - 1]) / 1000
#     return math.floor(res) >= 2


def start():
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath("independent-bay-250811-332458c28ecc.json")
    # print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])

    regular_load_process = start_regular_load()

    def authenticate():
        config.load_kube_config()
        auto_scale_api = client.AutoscalingV1Api()
        cluster_api = client.CoreV1Api()

        return auto_scale_api, cluster_api



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

    nodes_count = 0
    desire_pod_count = 0
    current_pods_count = 0
    active_pods_count = 0
    cpu_load = 0
    last_scale_time = None

    with safe_open(csv_file_name, 'w') as f:
        w = csv.writer(f, delimiter=',')
        # Probe test
        for index in range(1000000):

            try:
                print('sending probe')
                res_time = send_probe(END_POINT)
                print('revived probe')
            except Exception as e:
                print('retry - sending probe - {}'.format(e))
                res_time = send_probe(END_POINT)
                print('retry - revived probe')
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
                threshold = latest_attack_index+1000
                hard_reset_trigger = index > threshold
                if (index > 120 and cpu_load <= 56 and nodes_count > 2):
                    is_running_attack = False
                    if attack_process:
                        try:
                            print("killing attack process")
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
                if nodes_count == 3 and index > 50:
                    is_running_attack = True
                    latest_attack_index = index
                    print('init attack by POD COUNT on index = {}'.format(index))
                    attack_process = start_on_attack_phase()

            if index % 9 == 0:
                name = 'hpa-example-autoscaler'
                namespace = 'default'
                try:
                    print('Updating cluster info')
                    api_response = autoscale_api_instance.read_namespaced_horizontal_pod_autoscaler(name, namespace,
                                                                                                    pretty=True)
                    nodes_count = len(list(cluster_api.list_node().items))
                    active_pods_count = len(
                        [pod for pod in cluster_api.list_pod_for_all_namespaces(label_selector='app=hpa-example').items
                         if pod.status.phase == 'Running'])
                except Exception as e:
                    # TODO  -re authenticate
                    print('error trying to authenticate - {}'.format(e))
                    p = subprocess.Popen(['kubectl', 'get', 'hpa'],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print('BEFPRE p wait')
                    p.wait()
                    print('ACFTER p wait')
                    autoscale_api_instance, cluster_api = authenticate()
                    api_response = autoscale_api_instance.read_namespaced_horizontal_pod_autoscaler(name, namespace,
                                                                                                    pretty=True)
                    nodes_count = len(list(cluster_api.list_node().items))
                    active_pods_count = len(
                        [pod for pod in cluster_api.list_pod_for_all_namespaces(label_selector='app=hpa-example').items
                         if pod.status.phase == 'Running'])

                status = api_response.status
                current_pods_count = status.current_replicas
                desire_pod_count = status.desired_replicas
                cpu_load = status.current_cpu_utilization_percentage
                last_scale_time = status.last_scale_time
                print('Done Updating cluster info - {}\nactive: {}'.format(status, active_pods_count))

            # Get avarage time of the last x res and see if attack
            probe_time_tupples.append(res_time)

            headers = [
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
                    'current_pods_count',
                    'active_pods_count',
                    'desire_pod_count',
                    'cpu_load',
                    'node_count',
                    'current_power_off_attack',
                    #
                    'is running attach'

                ]

            stats = [
                index,  # time
                min(round(res_time, 1), 5),  # probe response time - flatten weird results
                # Attack
                avg_attack_res_time,
                mean_attack_res_time,
                per95_attack_res_time,
                per90_attack_res_time,
                # probe
                (sum(probe_time_tupples) / len(probe_time_tupples)),  # total avg res time
                mean(probe_time_tupples),  # total mea res time
                np.percentile(np.array(probe_time_tupples), 90),
                np.percentile(np.array(probe_time_tupples), 95),
                # HPA INFO
                current_pods_count,
                active_pods_count,
                desire_pod_count,
                cpu_load,  # Normalize
                nodes_count,
                (CONFIG['k']),
                # is
                int(is_running_attack),  # Nonmalize
                #
                last_scale_time
            ]
            if index == 0: # Add headers
                w.writerow(headers)

            w.writerow(stats)

            print(dict(zip(headers, stats)))



    print('config - {}'.format(CONFIG))
    if regular_load_process:
        try:
            print("killing regular_load_process")
            regular_load_process.kill()
            regular_load_process = None
        except Exception as e:
            print("kill regular_load_process - {}".format(e))


start()
