import uuid
import time
from functools import partial
from collections import Counter
from threading import Thread
from queue import Queue, Empty

class TaskManager:

    @staticmethod
    def hash_task(task):
        return hash(''.join(str(task.get(key, '')) for key in ('package', 'version', 'function')))

    def __init__(self):
        self.wait_interval = 0.01

        self.tasks = {}
        self.answers = {}

        self.unsent_tasks = []
        self.streams = {}

        self.task_performance = {}

    def get_tasks(self):
        return self.tasks

    def start_stream(self, ids, unordered=False):
        def fill_queue(queue, iterable):
            for item in iterable:
                queue.put(item)

        stream_id = str(uuid.uuid4())
        answer_queue = Queue()
        answer_gen = self.get_answers(ids, unordered=unordered)

        self.streams[stream_id] = {
            'generator': answer_gen,
            'queue': answer_queue,
            'worker': Thread(target=partial(fill_queue, answer_queue, answer_gen)),
            'left': len(ids)
        }
        self.streams[stream_id]['worker'].start()

        return stream_id

    def get_from_stream(self, stream_id):

        if stream_id not in self.streams:
            raise WrongIDException()

        answers = []
        while True:
            try:
                answers.append(self.streams[stream_id]['queue'].get_nowait())
            except Empty:
                break

        self.streams[stream_id]['left'] -= len(answers)
        last = self.streams[stream_id]['left'] == 0

        if last:
            self.streams.pop(stream_id)

        return answers, last

    def add_task(self, task):
        id_ = str(uuid.uuid4())
        self.tasks[id_] = task
        self.unsent_tasks.append(id_)

        return id_

    def get_answers(self, ids, unordered=False):
        if unordered:
            while ids:
                for id_ in ids.copy():
                    if id_ in self.answers:
                        ids.remove(id_)
                        yield self.answers.pop(id_)
                time.sleep(self.wait_interval) 
        else:
            for id_ in ids:
                while id_ not in self.answers:
                    time.sleep(self.wait_interval)
                yield self.answers.pop(id_)


    def get_task(self):
        while True:
            try:
                id_ = self.unsent_tasks.pop(0)
                break
            except IndexError:
                time.sleep(self.wait_interval)

        task = self.tasks[id_]

        return id_, task

    def add_answer(self, id_, answer, time=None):

        if id_ in self.tasks:
            task = self.tasks[id_]
            del self.tasks[id_]
        else:
            raise WrongIDException()

        hash_key = self.hash_task(task)

        self.answers[id_] = answer

        if time != None:
            self.task_performance.setdefault(hash_key, []).append(time)

    def estimate_runtime(self, hash_key):
        if hash_key in self.task_performance:
            times = self.task_performance[hash_key]
            return sum(times) / len(times)
        else:
            return 0

    def estimate_time_left(self):
        tasks = Counter(self.hash_task(self.tasks[id_]) for id_ in self.unsent_tasks).items()
        return sum(self.estimate_runtime(hash_key) * count for hash_key, count in tasks)


class NotReadyException(Exception):
    pass

class WrongIDException(Exception):
    pass
