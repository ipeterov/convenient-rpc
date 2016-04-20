from lib import API

api = API('http://localhost:5000/')

funcdesc = {'function': 'hash'}
argskwargs = {'args': ['qwe'*100]}

task = api.make_task(funcdesc, argskwargs)

# for answer in api.map_unordered(funcdesc, [argskwargs for _ in range(10)]):
#     print(answer)

for _ in range(1000):
    api.send_task(task)

print(api.estimate_time_left())