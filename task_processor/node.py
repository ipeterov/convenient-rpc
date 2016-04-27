import builtins
import multiprocessing
import importlib
import time
import argparse

import requests
from requests.compat import urljoin
from virtualenvapi.manage import VirtualEnvironment

def process_task(task_tuple):
    id_, function, args, kwargs = task_tuple
    if args == None:
        args = []
    if kwargs == None:
        kwargs = {}

    t = time.time()
    ret = function(*args, **kwargs)
    t = time.time() - t

    return id_, ret, t

class TaskProcessor:

    send_result_endpoint = 'worker/submit_answer'
    get_task_endpoint = 'worker/request_task'

    def __init__(self, server_addr):
        
        # This will throw an exception if run not from virtualenv
        self.env = VirtualEnvironment()

        self.server_addr = server_addr
        self.pool = multiprocessing.Pool()

    def send_result(self, id_, answer, time=None):
        data = {'id': id_, 'answer': answer}
        if not time == None:
            data['time'] = time
        r = requests.post(urljoin(self.server_addr, self.send_result_endpoint), json=data).json()
        # if r['sucsess'] == False:
            # raise Exception('Server did not accept the result')

    def get_function(self, function, package_name=None, version=None):
        if package_name:
            try: 
                package = importlib.import_module(package_name)
            except ImportError:
                if not version:
                    self.env.install(package_name)
                else:
                    self.env.install((package_name, version))
                package = importlib.import_module(package_name)
            return getattr(package, function)
        else:
            return getattr(builtins, function)

    def task_generator(self, check_interval=1):
        while True:
            try:
                r = requests.get(urljoin(self.server_addr, self.get_task_endpoint)).json()
            except:
                time.sleep(check_interval)
                continue
            
            if r['sucsess'] == True:
                task = r['task']
                function = self.get_function(task['function'], task.get('package', None), task.get('version', None))
                yield r['id'], function, task.get('args', []), task.get('kwargs', {})
            else:
                time.sleep(check_interval)
                continue

    def mainloop(self):
        for id_, answer, time in self.pool.imap_unordered(process_task, self.task_generator()):
            self.send_result(id_, answer, time)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A convenient-rpc node.')
    parser.add_argument('server_address')
    args = parser.parse_args()

    processor = TaskProcessor(args.server_address)
    processor.mainloop()
