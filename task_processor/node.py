import builtins
import multiprocessing
import importlib

import requests
from virtualenvapi.manage import VirtualEnvironment

def process_task(task_tuple):
    id_, function, args, kwargs = task_tuple
    if args == None:
        args = []
    if kwargs == None:
        kwargs = {}
    return id_, function(*args, **kwargs)

class TaskProcessor:

    def __init__(self, server_addr='http://control.us-west-2.elasticbeanstalk.com'):
        
        # This will throw an exception if run not from virtualenv
        self.env = VirtualEnvironment()

        self.server_addr = server_addr
        self.pool = multiprocessing.Pool()

    def send_result(self, id_, answer):
        data = {'id': id_, 'answer': answer}
        r = requests.post(self.server_addr + '/submit_answer', data=data).json()
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

    def task_generator(self):
        while True:
            try:
                r = requests.get(self.server_addr + '/request_task').json()
            except:
                continue
            task = r['task']
            if r['sucsess'] == True:
                function = self.get_function(task['function'], task.get('package', None), task.get('version', None))
                yield r['id'], function, task['args'], task['kwargs']

    def mainloop(self):
        for id_, answer in self.pool.imap_unordered(process_task, self.task_generator()):
            self.send_result(id_, answer)

if __name__ == '__main__':
    processor = TaskProcessor()
    processor.mainloop()
