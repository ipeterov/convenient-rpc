from base64 import b64encode


import cloudpickle
import requests
from requests.compat import urljoin


class API:

    send_task_endpoint = 'user/submit_tasks'
    get_answer_endpoint = 'user/request_answers'
    get_stream_endpoint = 'user/request_from_stream'
    estimate_time_left_endpoint = 'user/estimate_time_left'

    @staticmethod
    def make_tasks(function, argskwargslist=[]):
        if callable(function):
            tasks = {
                'function': b64encode(cloudpickle.dumps(function)).decode('utf-8'),
                'mode': 'pickle'
            }
        elif isinstance(function, dict):
            tasks = {
                'function': function.copy(),
                'mode': 'funcdesc'
            }

        tasks['argskwargslist'] = argskwargslist
        return tasks

    def __init__(self, server_addr, check_interval=1, stream_chunksize=5):
        self.check_interval = check_interval
        self.stream_chunksize = stream_chunksize
        self.server_addr = server_addr

    def post(self, endpoint, **kwargs):
        r = requests.post(urljoin(self.server_addr, endpoint), json=kwargs).json()
        if r['sucsess']:
            return r
        else:
            raise RuntimeError('Server returned sucsess != True')

    def get(self, endpoint):
        r = requests.get(urljoin(self.server_addr, endpoint)).json()
        if r['sucsess']:
            return r
        else:
            raise RuntimeError('Server returned sucsess != True')

    def send_tasks(self, tasks):
        r = self.post(self.send_task_endpoint, **tasks)
        return r['ids']

    def get_answers(self, ids, stream=True, unordered=False):
        if stream:
            r = self.post(self.get_answer_endpoint, ids=ids, start_stream=True, unordered=unordered)
            stream_id = r['stream_id']

            while True:
                r = self.post(self.get_stream_endpoint, stream_id=stream_id)

                for answer in r.get('answers', []):
                    yield answer

                if r['last']:
                    break
        else:
            r = self.post(self.get_answer_endpoint, ids=ids, unordered=unordered)
            for answer in r.get('answers', []):
                yield answer

    def estimate_time_left(self):
        r = self.get(self.estimate_time_left_endpoint)
        return r['time']

    def map(self, function, items, unordered=False):
        tasks = self.make_tasks(function, [{'args': [item]} for item in items])
        ids = self.send_tasks(tasks)
        return self.get_answers(ids, unordered=unordered)
    
    def apply(self, function, *args, **kwargs):
        tasks = self.make_tasks(function, argskwargslist=[{'args': args, 'kwargs': kwargs}])
        ids = self.send_tasks(tasks)
        return list(self.get_answers(ids, stream=False))[0]