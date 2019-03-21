import subprocess

import requests
from ratelimit import limits, sleep_and_retry

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

    END_POINT = 'http://130.211.200.247:31001/service'

    def __init__(self, args):
        super(Attacker, self).__init__()
        self.k = args.get('k', 1)
        self.n = args.get('n', 1)
        self.t = 0
        self.t_on = args.get('t_on', 100)
        self.t_off = args.get('t_off', 330)

        self.i_up = 0
        self.i_down = 0
        self.w_up = 0
        self.w_down = 0

        self.is_attack_on = False

        self.attack_process = None

    # Probe packet
    def start_attack(self):
        self.attack_process = subprocess.Popen(
            ['loadtest', Attacker.END_POINT,
             '-t', str(self.t_on),
             '-c', str(self.k),
             '--rps', str(self.k)
             ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.is_attack_on = True
        print('ATTACK IS ON')

    def stop_attack(self):
        self.is_attack_on = False
        if self.attack_process:
            try:
                self.attack_process.kill()
                self.attack_process = None
            except Exception as e:
                print("kill attack fail - {}".format(e))

    @sleep_and_retry
    @limits(calls=1, period=1)
    def send_probe(url):
        response = requests.get(url)
        if response.status_code != 200:
            res_time = 5
        else:
            res_time = response.elapsed.total_seconds()
        return res_time

    def start(self):
        pass
