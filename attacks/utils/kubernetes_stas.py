from .subutils import Base
from kubernetes import client, config
import subprocess

class KubernetesUtils(Base):
    def __init__(self, args):
        super(KubernetesUtils, self).__init__()
        self.auto_scale_api = None
        self.cluster_api = None
        self.name = args.get('name','hpa-example-autoscaler')
        self.namespace = args.get('namespace','default')
        self.stats = []
        self.curr_state = {}
        self.headers = [# Note order is important later for csv
            'current_pods_count',
            'active_pods_count',
            'desire_pod_count',
            'last_scale_time',
            'cpu_load',
            'node_count',
        ]

        self._authenticate()

    # Private
    def _authenticate(self):
        config.load_kube_config()
        self.auto_scale_api = client.AutoscalingV1Api()
        self.cluster_api = client.CoreV1Api()

    def _sample_autoscale(self):
        api_response = self.autoscale_api_instance\
            .read_namespaced_horizontal_pod_autoscaler(self.name, self.namespace, pretty=True)

        return api_response.status

    def _sample_autoscale_fallbacK(self):
        p = subprocess.Popen(['kubectl', 'get', 'hpa'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('FALLBACAK AUTOSCALE TRY CLI - START PROCESS')
        p.wait()
        print('FALLBACAK AUTOSCALE TRY CLI - END PROCESS')

        self.authenticate()

        api_response = self.autoscale_api_instance \
            .read_namespaced_horizontal_pod_autoscaler(self.name, self.namespace, pretty=True)
        return api_response.status

    def _sample_cluster(self):
        nodes_count = len(list(self.cluster_api.list_node().items))
        active_pods_count = len(
            [pod for pod in self.cluster_api.list_pod_for_all_namespaces(label_selector='app=hpa-example').items
             if pod.status.phase == 'Running'])

        return {"nodes_count": nodes_count, "active_pods_count": active_pods_count}



    def _sample(self):
        try:
            autoscale_sample = self._sample_autoscale()
            claster_sample = self._sample_cluster()

            current_pods_count = autoscale_sample.current_replicas
            desire_pod_count = autoscale_sample.desired_replicas
            cpu_load = autoscale_sample.current_cpu_utilization_percentage
            last_scale_time = autoscale_sample.last_scale_time
            nodes_count = claster_sample["nodes_count"]
            active_pods_count = claster_sample["active_pods_count"]
        except Exception as e:
            self._authenticate()
            autoscale_sample = self._sample_autoscale_fallbacK()
            claster_sample = self._sample_cluster()

            current_pods_count = autoscale_sample.current_replicas
            desire_pod_count = autoscale_sample.desired_replicas
            cpu_load = autoscale_sample.current_cpu_utilization_percentage
            last_scale_time = autoscale_sample.last_scale_time
            nodes_count = claster_sample["nodes_count"]
            active_pods_count = claster_sample["active_pods_count"]

        self.stats.append([
            current_pods_count,
            active_pods_count
            desire_pod_count,
            cpu_load,
            last_scale_time,
            nodes_count,
        ])
        self.curr_state = {
            'current_pods_count': current_pods_count,
            'active_pods_count': active_pods_count,
            'desire_pod_count': desire_pod_count,
            'last_scale_time': last_scale_time,
            'cpu_load': cpu_load,
            'node_count':nodes_count,
        }
