import unittest

from lib.tasks import *

manager = TaskManager()

class TestManager(unittest.TestCase):

    def test_estimate_runtime(self):
        import random

        task = {
            'package': 1,
            'version': 2,
            'function': 3,
        }

        task2 = {
            'package': 1,
            'version': 2,
            'function': 2,
        }

        manager = TaskManager()

        for _ in range(10):
            manager.add_task(task)

        for i in range(10):
            id_, answer = manager.get_task()
            manager.add_answer(id_, 1, time=i+2)

        for _ in range(9):
            manager.add_task(task)

        self.assertEqual(manager.estimate_runtime(manager.hash_task(task)), 6.5)
        self.assertEqual(manager.estimate_time_left(), 58.5)

if __name__ == '__main__':
    unittest.main(verbosity=2)