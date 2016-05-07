import json

from flask import Flask, Response, jsonify, request

from lib.tasks import TaskManager, WrongIDException
from lib.passwd import PasswordManager, UserPresentException

app = Flask(__name__)
pass_manager = PasswordManager()
task_manager = TaskManager()

@app.route("/user/register_user", methods=['POST'])
@pass_manager.requires_auth
def register_user():
    r = request.get_json(force=True)

    try:
        pass_manager.register(r['username'], r['password'])
    except UserPresentException:
        return jsonify(sucsess=False, reason='User with this login is already present')

    return jsonify(sucsess=True)

@app.route("/user/submit_tasks", methods=['POST'])
@pass_manager.requires_auth
def submit_tasks():
    r = request.get_json(force=True)

    if 'argskwargslist' not in r:
        return jsonify(sucsess=False, reason='argskwargslist is empty')

    # argskwargslist: [{'args': [1, 'eggs'], 'kwargs': {'spam': True}}, {}]
    ids = []
    for argskwargs in r.pop('argskwargslist'): # we're popping argskwargslist so we can use r as a template
        task = r.copy()
        task.update(argskwargs)
        ids.append(task_manager.add_task(task))    

    return jsonify(sucsess=True, ids=ids)

@app.route("/user/request_answers", methods=['POST'])
@pass_manager.requires_auth
def request_answers():

    r = request.get_json(force=True)

    start_stream = r.get('start_stream', False)
    unordered = r.get('unordered', False)
    ids = r.get('ids', [])

    if start_stream:
        return jsonify(sucsess=True, stream_id=task_manager.start_stream(ids, unordered=unordered))
    else:
        return jsonify(sucsess=True, answers=list(task_manager.get_answers(ids, unordered=unordered)))

@app.route("/user/request_from_stream", methods=['POST'])
@pass_manager.requires_auth
def request_from_stream():
    r = request.get_json(force=True)

    stream_id = r['stream_id']

    try:
        answers, last = task_manager.get_from_stream(stream_id)
        return jsonify(sucsess=True, answers=answers, last=last)
    except WrongIDException:
        return jsonify(sucsess=False, reason='There is no stream with this ID')

@app.route("/user/estimate_time_left", methods=['GET'])
@pass_manager.requires_auth
def estimate_time_left():
    return jsonify(sucsess=True, time=task_manager.estimate_time_left())

@app.route("/worker/request_task", methods=['GET'])
@pass_manager.requires_auth
def request_task():
    id_, task = task_manager.get_task()
    return jsonify(sucsess=True, id=id_, task=task)

@app.route("/worker/submit_answer", methods=['POST'])
@pass_manager.requires_auth
def submit_answer():

    r = request.get_json()

    if r['sucsess']:
        id_ = r['id']
        answer = r['answer']
        time = r.get('time', None)

        try:
            task_manager.add_answer(id_, answer, time)
            return jsonify(sucsess=True)
        except WrongIDException:
            return jsonify(sucsess=False, reason='There was no task with this ID')
    else:
        print('Task with id={} failed with: "{}".'.format(r['id'], r['exception']))
        return jsonify(sucsess=True)


if __name__ == "__main__":
    try:
        pass_manager.register('admin', 'admin')
    except UserPresentException:
        pass

    app.run(debug=True, threaded=True, host='0.0.0.0')
