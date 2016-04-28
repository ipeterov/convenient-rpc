import json
import uuid
from itertools import islice
from functools import partial
from threading import Thread
from queue import Queue, Empty

from flask import Flask, Response, jsonify, request

from lib import *


app = Flask(__name__)
manager = TaskManager()
streams = {}

def fill_queue(queue, iterable):
    for item in iterable:
        queue.put(item)

@app.route("/user/submit_tasks", methods=['POST'])
def submit_tasks():
    r = request.get_json(force=True)

    if 'argskwargslist' not in r:
        return jsonify(sucsess=False, reason='argskwargslist is empty')

    # argskwargslist: [{'args': [1, 'eggs'], 'kwargs': {'spam': True}}, {}]
    ids = []
    for argskwargs in r.pop('argskwargslist'): # we're popping argskwargslist so we can use r as a template
        task = r.copy()
        task.update(argskwargs)
        ids.append(manager.add_task(task))    

    return jsonify(sucsess=True, ids=ids)

@app.route("/user/request_answers", methods=['POST'])
def request_answers():

    r = request.get_json(force=True)

    start_stream = r.get('start_stream', False)
    unordered = r.get('unordered', False)
    ids = r.get('ids', [])

    answer_gen = manager.get_answers(ids, unordered=unordered)

    if start_stream:

        stream_id = str(uuid.uuid4())
        answer_queue = Queue()

        streams[stream_id] = {
            'generator': answer_gen,
            'queue': answer_queue,
            'worker': Thread(target=partial(fill_queue, answer_queue, answer_gen)),
            'left': len(ids)
        }
        streams[stream_id]['worker'].start()

        return jsonify(sucsess=True, stream_id=stream_id)
    else:
        return jsonify(sucsess=True, answers=list(answer_gen))

@app.route("/user/request_from_stream", methods=['POST'])
def request_from_stream():
    r = request.get_json(force=True)

    stream_id = r['stream_id']

    if stream_id not in streams:
        return jsonify(sucsess=False, reason='Stream with this id does not exist')

    answers = []
    while True:
        try:
            answers.append(streams[stream_id]['queue'].get_nowait())
        except Empty:
            break

    streams[stream_id]['left'] -= len(answers)
    last = streams[stream_id]['left'] == 0

    if last:
        streams.pop(stream_id)

    return jsonify(sucsess=True, answers=answers, last=last)

@app.route("/user/estimate_time_left", methods=['GET'])
def estimate_time_left():
    return jsonify(sucsess=True, time=manager.estimate_time_left())

@app.route("/admin/show_tasks", methods=['GET'])
def show_tasks():
    return jsonify(manager.get_tasks())

@app.route("/worker/request_task", methods=['GET'])
def request_task():
    id_, task = manager.get_task()
    return jsonify(sucsess=True, id=id_, task=task)

@app.route("/worker/submit_answer", methods=['POST'])
def submit_answer():

    r = request.get_json()

    if r['sucsess']:
        id_ = r['id']
        answer = r['answer']
        time = r.get('time', None)

        try:
            manager.add_answer(id_, answer, time)
            return jsonify(sucsess=True)
        except WrongIDException:
            return jsonify(sucsess=False, reason='There was no task with this ID')
    else:
        print('Task with id={} failed with: "{}".'.format(r['id'], r['exception']))
        return jsonify(sucsess=True)


if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0')
