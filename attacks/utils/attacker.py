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


class JMeterAttacker(object):
    """docstring for Tester."""

    def __init__(self, args):
        super(JMeterAttacker, self).__init__()
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

        self.attack_processes = []

    def _jmeter_command(self, test_case):
        JMETER = ["./apache-jmeter-5.1.1/bin/jmeter"]
        FLAGS = ['-n'] + ['-t {}'.format(test_case)]  # + ['-l {}_res.csv'.format('test.test')]
        return JMETER + FLAGS

    # Probe packet
    def start_attack(self, jmeter_test_case):
        p =  subprocess.Popen(
            self._jmeter_command(jmeter_test_case),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.attack_processes.append(p)
        self.is_attack_on = True
        print('START ATTACK PROCESS - {}'.format(p.pid))

    def stop_attack(self):
        self.is_attack_on = False

        if len(self.attack_processes) == 0:
            return

        def kill(p):
            try:
                p.kill()
                print('ATTACK PROCESS KILLED - {}'.format(p.pid))
            except Exception as e:
                print("kill attack fail - {}".format(e))

        for p in self.attack_processes:
            kill(p)

        self.attack_processes = []
        print('ALL ATTACK PROCESSES ARE OFF')


    @sleep_and_retry
    @limits(calls=1, period=1)
    def send_probe(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            res_time = 5
        else:
            res_time = response.elapsed.total_seconds()
        return res_time

    def start(self):
        pass
