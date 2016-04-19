import requests
import time


class API:
    @staticmethod
    def make_task(function_description, argskwargs):
        task = function_description.copy()
        task['args'] = argskwargs.get('args', [])
        task['kwargs'] = argskwargs.get('kwargs', {})
        return task

    def __init__(self, server_addr):
        self.server_addr = server_addr

    def send_task(self, task):
        response = requests.post(self.server_addr, data=task).json()

        if response['sucsess']:
            return response['id']
        else:
            raise RuntimeError('Server returned sucsess != True')

    def get_answer(self, id_):
        params = {'id': id_}
        response = requests.get(self.server_addr, params=params).json()
        return response['sucsess'], response.get('answer', None)

    def map_unordered(self, function_description, argskwargslist):
        ids = set()
        for task in (make_task(function_description, argskwargs) for argskwargs in argskwargslist):
            ids.add(self.send_task(task))

        while ids:
            for id_ in ids.copy():
                sucsess, answer = self.get_answer(id_)
                if sucsess:
                    ids.remove(id_)
                    yield answer

    def map(self, function_description, argskwargslist, check_interval=0.1):
        ids = set()
        for task in (make_task(function_description, argskwargs) for argskwargs in argskwargslist):
            ids.add(self.send_task(task))

        for id_ in ids:
            while True:
                sucsess, answer = self.get_answer(id_)
                if sucsess:
                    yield answer
                    break
                else:
                    time.sleep(check_interval)