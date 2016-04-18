import uuid
from threading import RLock
from queue import Queue

class TaskManager:

    @staticmethod
    def hash_task(task):
        return hash(''.join(str(task[key]) for key in ('package', 'version', 'function')))

    def __init__(self):
        self.tasks = {}
        self.tasks_lock = RLock()

        self.answers = {}
        self.answers_lock = RLock()

        self.task_performance = {}
        self.task_performance_lock = RLock()

        self.unsent_tasks = Queue()

    def add_task(self, task):
        id_ = str(uuid.uuid4())
        with self.tasks_lock:
            self.tasks[id_] = task
            self.unsent_tasks.put(id_)
        return id_

    def get_answer(self, id_):
        with self.answers_lock:
            ready = id_ in self.answers

        if ready:
            return self.answers.pop(id_)
        else:
            raise NotReadyException()

    def get_task(self):
        id_ = self.unsent_tasks.get()

        with self.tasks_lock:
            task = self.tasks[id_]

        return id_, task

    def add_answer(self, id_, answer, time=None):
        with self.tasks_lock:
            task = self.tasks[id_]
            hash_key = self.hash_task(task)

            if id_ in self.tasks:
                del self.tasks[id_]
            else:
                raise WrongIDException()

        with self.answers_lock:
            self.answers[id_] = answer

        if time != None:
            with self.task_performance_lock:
                self.task_performance.setdefault(hash_key, []).append(time)

    def estimate_runtime(self, task):
        hash_key = self.hash_task(task)

        with self.task_performance_lock:
            if hash_key in self.task_performance:
                times = self.task_performance[hash_key]
                return sum(times) / len(times)


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
    