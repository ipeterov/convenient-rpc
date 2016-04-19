import requests


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

    def imap_byid(self, function_description, argskwargslist):
        ids = set()
        for task in (make_task(function_description, argskwargs) for argskwargs in argskwargslist):
            ids.add(self.send_task(task))

        while ids:
            for id_ in ids.copy():
                sucsess, answer = self.get_answer(id_)
                if sucsess:
                    ids.remove(id_)
                    yield id_, answer