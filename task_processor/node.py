import builtins
import multiprocessing
import importlib
import time

import requests
from requests.compat import urljoin
from virtualenvapi.manage import VirtualEnvironment

def process_task(task_tuple):
    id_, function, args, kwargs = task_tuple
    if args == None:
        args = []
    if kwargs == None:
        kwargs = {}
    return id_, function(*args, **kwargs)

class TaskProcessor:

    send_result_endpoint = 'worker/submit_answer'
    get_task_endpoint = 'worker/request_task'

    def __init__(self, server_addr):
        
        # This will throw an exception if run not from virtualenv
        self.env = VirtualEnvironment()

        self.server_addr = server_addr
        self.pool = multiprocessing.Pool()

    def send_result(self, id_, answer):
        data = {'id': id_, 'answer': answer}
        r = requests.post(urljoin(self.server_addr, self.send_result_endpoint), json=data).json()
        if r['sucsess'] == False:
            raise Exception('Server did not accept the result')

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
                yield r['id'], function, task['args'], task['kwargs']
            else:
                time.sleep(check_interval)
                continue

    def mainloop(self):
        for id_, answer in self.pool.imap_unordered(process_task, self.task_generator()):
            self.send_result(id_, answer)

if __name__ == '__main__':
    processor = TaskProcessor('http://localhost:5000/')
    processor.mainloop()
