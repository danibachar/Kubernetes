from locust import HttpLocust, TaskSet, task
from datetime import datetime
import json
import subprocess


class UserBehavior(TaskSet):
    # def on_start(self):
    #     """ on_start is called when a Locust start before any task is scheduled """

    # def on_stop(self):
    #     """ on_stop is called when the TaskSet is stopping """

    @task(1)
    def find_bubbles(self):

        # url = _get_kubernetes_url()
        # print("query url {}".format(url))
        # print('befores - {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        res = self.client.get("/7")
        # print('after - {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        # print("Response status code:", res.status_code)
        print("Response text:", res.text)
        print("Time:", res.elapsed)
        # print("Response: {}".format(res), res)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 5000