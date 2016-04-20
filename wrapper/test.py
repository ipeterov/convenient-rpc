from lib import API

api = API('http://localhost:5000/')

funcdesc = {'function': 'id'}
argskwargs = {'args': ['qwe']}

for answer in api.map_unordered(funcdesc, [argskwargs for _ in range(10)]):
    print(answer)