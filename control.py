import json
from itertools import islice, zip_longest

from flask import Flask, jsonify, request

from lib import *


app = Flask(__name__)
manager = TaskManager()


@app.route("/submit_task", methods=['POST'])
def submit_task():
    argslist = json.loads(request.args.get('argslist', '[]'))
    kwargslist = json.loads(request.args.get('kwargslist', '[]'))
    ids = []
    for args, kwargs in islice(zip_longest(argslist, kwargslist, fillvalue=None), max(map(len, (argslist, kwargslist)))):
        task = {
            'package': request.args.get('package', None),
            'version': request.args.get('version', None),
            'function': request.args['function'],
            'args': args,
            'kwargs': kwargs
        }
        id_ = manager.add_task(task)
        ids.append(id_)

    return jsonify(sucsess=True, ids=ids)

@app.route("/request_answer", methods=['GET'])
def request_answer():
    id_ = request.args['id']
    blocking = int(request.args.get('blocking', '1'))

    if blocking:
        while True:
            try:
                answer = manager.get_answer(id_)
                break
            except NotReadyException:
                pass
        return jsonify(sucsess=True, answer=answer)
    else:
        try:
            return jsonify(sucsess=True, answer=manager.get_answer(id_))
        except NotReadyException:
            return jsonify(sucsess=False, reason='Task with this ID is not ready yet')

@app.route("/request_task", methods=['GET'])
def request_task():
    id_, task = manager.get_task()
    return jsonify(sucsess=True, id=id_, task=task)

@app.route("/submit_answer", methods=['POST'])
def submit_answer():
    id_ = request.values['id']
    answer = request.values['answer']
    try:
        manager.add_answer(id_, answer)
        return jsonify(sucsess=True)
    except WrongIDException:
        return jsonify(sucsess=False, reason='There was no task with this ID')


if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0')
