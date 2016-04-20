import time

import requests
from requests.compat import urljoin


class API:

    send_task_endpoint = 'user/submit_task'
    get_answer_endpoint = 'user/request_answer'
    estimate_time_left_endpoint = 'user/estimate_time_left'

    @staticmethod
    def make_task(function_description, argskwargs):
        task = function_description.copy()
        task['args'] = argskwargs.get('args', [])
        task['kwargs'] = argskwargs.get('kwargs', {})
        return task

    def __init__(self, server_addr):
        self.server_addr = server_addr

    def send_task(self, task):
        response = requests.post(urljoin(self.server_addr, self.send_task_endpoint), json=task).json()

        if response['sucsess']:
            return response['id']
        else:
            raise RuntimeError('Server returned sucsess != True')

    def get_answer(self, id_):
        params = {'id': id_}
        response = requests.get(urljoin(self.server_addr, self.get_answer_endpoint), params=params).json()
        return response['sucsess'], response.get('answer', None)

    def estimate_time_left(self):
        response = requests.get(urljoin(self.server_addr, self.estimate_time_left_endpoint))
        response = response.json()
        return response['time']

    def map_unordered(self, function_description, argskwargslist, check_interval=1):
        ids = set()
        for task in (self.make_task(function_description, argskwargs) for argskwargs in argskwargslist):
            ids.add(self.send_task(task))

        while ids:
            for id_ in ids.copy():
                sucsess, answer = self.get_answer(id_)
                if sucsess:
                    ids.remove(id_)
                    yield answer
                else:
                    time.sleep(check_interval)

    def map(self, function_description, argskwargslist, check_interval=1):
        ids = set()
        for task in (self.make_task(function_description, argskwargs) for argskwargs in argskwargslist):
            ids.add(self.send_task(task))

        for id_ in ids:
            while True:
                sucsess, answer = self.get_answer(id_)
                if sucsess:
                    yield answer
                    break
                else:
                    time.sleep(check_interval)