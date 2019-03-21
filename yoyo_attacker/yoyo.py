from time import time

from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):
    @task(1)
    def my_test(self):
        res = self.client.get("/service")


class ConstantWaitTimeTaskSet(TaskSet):
    wait_time = 1000

    def __init__self(self, *args, **kwargs):
        super(TaskSet, self).__init__(*args, **kwargs)
        self._time_waited = 0

    def wait(self):
        t = max(0, self.wait_time - self._time_waited) / 1000.0
        self._sleep(t)
        self._time_waited = 0

    def get(self, *args, **kwargs):
        start = time()
        response = self.locust.cient.get(*args, **kwargs)
        self._time_waited += (time() - start) * 1000
        return response

    @task(1)
    def my_test(self):
        res = self.client.get("/4")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    # We decided on tihs user behaviour to enable better testing,
    # With this configuration 1 user will produce 1 RPS
    # So if we want to get 1000 RPS, all we need to do is spinn 1000 Users
    # min_wait = 1000
    # max_wait = 1000
    min_wait = 60000
    max_wait = 60000
