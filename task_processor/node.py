import builtins
import multiprocessing
import importlib
import time
import argparse
import pickle
from base64 import b64decode

import requests
from requests.auth import HTTPBasicAuth
from requests.compat import urljoin
from requests.exceptions import ConnectionError
from virtualenvapi.manage import VirtualEnvironment


def get_function(task):

    mode = task.get('mode', 'funcdesc')

    if mode == 'funcdesc':
        funcdesc = task['function']

        name = funcdesc['name']
        package_name = funcdesc.get('package', None)
        version = funcdesc.get('version', None)
        
        if package_name:
            try: 
                package = importlib.import_module(package_name)
            except ImportError:
                if not version:
                    env.install(package_name)
                else:
                    env.install((package_name, version))
                package = importlib.import_module(package_name)
            return getattr(package, name)
        else:
            return getattr(builtins, name)

    elif mode == 'pickle':
        return pickle.loads(b64decode(task['function'].encode('utf-8')))

def process_task(r):
    task = r['task']
    result = {
        'id': r['id']
    }
    function = get_function(task)
    args, kwargs = task.get('args', []), task.get('kwargs', {})

    try:
        t = time.time()
        result['answer'] =  function(*args, **kwargs)
        result['time'] = time.time() - t
        result['sucsess'] = True
    except Exception as e:
        result['exception'] = str(e)
        result['sucsess'] = False

    return result

class TaskProcessor:

    send_result_endpoint = 'worker/submit_answer'
    get_task_endpoint = 'worker/request_task'

    def __init__(self, server_addr, login, password):
        self.server_addr = server_addr
        self.login = login
        self.password = password

        self.pool = multiprocessing.Pool()

    def request(self, method, endpoint, **kwargs):
        response = requests.request(
            method,
            urljoin(self.server_addr, endpoint),
            auth=HTTPBasicAuth(self.login, self.password),
            **kwargs
        )

        if response.status_code == 401:
            raise InvalidCredentialsException('Server did not accept the credentials you specified')

        r = response.json()

        if r['sucsess']:
            return r
        else:
            raise RuntimeError('Server returned sucsess != True')

    def post(self, endpoint, **kwargs):
        return self.request('POST', json=kwargs)

    def get(self, endpoint):
        return self.request('GET', endpoint)

    def send_result(self, **kwargs):
        r = self.post(self.send_result_endpoint, **kwargs)

    def task_generator(self, check_interval=1):
        while True:
            try:
                r = self.get(self.get_task_endpoint)
            except ConnectionError:
                time.sleep(check_interval)
                continue
            
            if r['sucsess'] == True:
                yield r
            else:
                time.sleep(check_interval)
                continue

    def mainloop(self):
        for result in self.pool.imap_unordered(process_task, self.task_generator()):
            self.send_result(**result)


class InvalidCredentialsException(Exception):
    pass


if __name__ == '__main__':
    # This will throw an exception if run not from virtualenv
    env = VirtualEnvironment()

    parser = argparse.ArgumentParser(description='A convenient-rpc node.')
    parser.add_argument('server_address')
    parser.add_argument('login')
    parser.add_argument('password')
    args = parser.parse_args()

    processor = TaskProcessor(args.server_address, args.login, args.password)
    processor.mainloop()
