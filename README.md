# convenient-rpc

It's a project that allows to call functions on many remote machines (workers). Basically, you specify args, function, module name (and package, if needed), it installs it and imports modules on all the workers, passes args to the function and gives you your result.

## Example

Import it like that:

    from wrapper import API

    api = API('mytaskserver.somedomain')

Use it like that:

    def double(n):
        return n*2

    for result in api.map(double, range(3)):
        print(result)

    > 0  
    > 2
    > 4

It can also operate with function descriptions (just dictionaries describing how to get the function), if you need to use a module from PyPi, or from python stdlib:

    # All the options except for "function" are optional.
    # "module" is the thing that you import, 
    # "package" and "package_version" are the things you pass to pip.

    funcdesc = {
        # Let's use a PyPi package
        'package': 'entropy',
        'module': 'entropy',
        'function': 'shannon_entropy'
    }

    for result in api.map(funcdesc, ('spam', 'W2u)l1', '00000')):
        print(result)

    > 0.25  
    > 0.32312031562255994
    > 0.0

Note that functions can return only json-serializable objects. This is temporary, soon I will use `marshal` or `pickle` to be able to return more complicated stuff.

That this is an early alpha version, so stuff may brake / change quicky!

## Deployment

You'll have to install `wrapper` as a python module, launch `task_server` at one machine and launch `task_process` at all the worker machines. Sounds complicated, but I'm going to supply Docker images for it to make deploying such a thing on AWS (or any other hoster that supports Docker) pretty simple.