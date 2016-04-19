import uuid
from collections import Counter

class TaskManager:

    @staticmethod
    def hash_task(task):
        return hash(''.join(str(task[key]) for key in ('package', 'version', 'function')))

    def __init__(self):
        self.tasks = {}
        self.answers = {}

        self.unsent_tasks = []

        self.task_performance = {}

    def add_task(self, task):
        id_ = str(uuid.uuid4())
        self.tasks[id_] = task
        self.unsent_tasks.append(id_)

        return id_

    def get_answer(self, id_):
        if id_ in self.answers:
            return self.answers.pop(id_)
        else:
            raise NotReadyException()

    def get_task(self):
        id_ = self.unsent_tasks.pop(0)
        task = self.tasks[id_]

        return id_, task

    def add_answer(self, id_, answer, time=None):
        task = self.tasks[id_]
        hash_key = self.hash_task(task)

        if id_ in self.tasks:
            del self.tasks[id_]
        else:
            raise WrongIDException()

        self.answers[id_] = answer

        if time != None:
            self.task_performance.setdefault(hash_key, []).append(time)

    def estimate_runtime(self, hash_key):
        if hash_key in self.task_performance:
            times = self.task_performance[hash_key]
            return sum(times) / len(times)

    def estimate_time_left(self):
        tasks = Counter(self.hash_task(self.tasks[id_]) for id_ in self.unsent_tasks).items()
        return sum(self.estimate_runtime(hash_key) * count for hash_key, count in tasks)


class NotReadyException(Exception):
    pass

class WrongIDException(Exception):
    pass


if __name__ == '__main__':
    import random

    task = {
        'package': 1,
        'version': 2,
        'function': 3,
    }

    manager = TaskManager()

    for _ in range(10):
        manager.add_task(task)

    for _ in range(10):
        id_, answer = manager.get_task()
        manager.add_answer(id_, 1, time=random.uniform(8, 12))

    print(manager.estimate_runtime(task))
    