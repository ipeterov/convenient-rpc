import json

from flask import Flask, jsonify, request

from lib import *


app = Flask(__name__)
manager = TaskManager()


@app.route("/user/submit_task", methods=['POST'])
def submit_task():
    task = request.json()
    id_ = manager.add_task(task)

    return jsonify(sucsess=True, id=id_)

@app.route("/user/request_answer/<id_>", methods=['GET'])
def request_answer(id_):
    try:
        return jsonify(sucsess=True, answer=manager.get_answer(id_))
    except NotReadyException:
        return jsonify(sucsess=False, reason='Task with this ID is not ready yet')

@app.route("/user/estimate_time_left", methods=['GET'])
def estimate_time_left():
    return jsonify(sucsess=True, time=manager.estimate_time_left())

@app.route("/worker/request_task", methods=['GET'])
def request_task():
    id_, task = manager.get_task()
    return jsonify(sucsess=True, id=id_, task=task)

@app.route("/worker/submit_answer", methods=['POST'])
def submit_answer():
    r = request.json()

    id_ = r['id']
    answer = r['answer']

    try:
        manager.add_answer(id_, answer)
        return jsonify(sucsess=True)
    except WrongIDException:
        return jsonify(sucsess=False, reason='There was no task with this ID')


if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0')
