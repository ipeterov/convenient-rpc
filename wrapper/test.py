from lib import API


api = API('http://localhost:5000/')

funcdesc = {'function': 'hash'}
# funcdesc = {'function': 'shannon_entropy', 'package': 'entropy', 'module': 'entropy'}
# argskwargs = {'args': ['qwe'*100]}

# task = api.make_task(funcdesc, argskwargs)

for answer in api.map(funcdesc, ('qwe{}'.format(n) for n in range(100)), unordered=True):
    print(answer)

# print(api.apply(funcdesc, 'qwe'))

# for _ in range(1000):
#     api.send_task(task)

# print(api.estimate_time_left())
