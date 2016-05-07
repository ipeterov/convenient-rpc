from lib import API

api = API('http://localhost:5000/')

# All the options except for "name" are optional.
# "module" is the thing that you import, 
# "package" and "package_version" are the things you pass to pip.

funcdesc = {'name': 'hash'}
# funcdesc = {
#     # Let's use some package from PyPi
#     'package': 'entropy',
#     'module': 'entropy',
#     'name': 'shannon_entropy'
# }

# items = ('qwe{}'.format(n) for n in range(10000))
items = ('spam', 'W2u)l1', '00000')

def double(n):
    return n*2

for result in api.map(double, items):
    # Do stuff with the structure our function returned
    print(result)

# api.apply(funcdesc, 1, 2)