# convenient-rpc

It's a project that allows to call functions on many remote machines (workers). Basically, you specify args, function, module name (and package, if needed), it installs it and imports modules on all the workers, passes args to the function and gives you your result.

You'll have to install wrapper as a python module, launch `task_server` at one machine and launch `task_process` at all the workers. Sounds complicated, but I will supply Docker images for it, so deploying such a thing on AWS (or any other hoster that supports Docker) will be pretty simple.

Then you will be able to use it like this:

    from wrapper import API

    api = API('mytaskserver.somedomain')
    
    # All the options except for "function" are optional.
    # "module" is the thing that you import, 
    # "package" and "pacakge_version" are the
    # things you pass to pip.
    function_description = {
        "package_version": "1.3",
        "package": "my_package",
        "module": "foo_module",
        "function": "foo"
    }
    
    argskwargslist = [
        [
            [42, 1], 
            {
                "bar": True,
                "spam": False
            }
        ],
    
        [
            [13, 2], 
            {
                "bar": False,
                "spam": True
            }
        ],
    ]

    for result in api.map(function_description, argskwargslist):
        # Do stuff with the structure our function returned
        print(result)

Note that it accepts not functions themselves, but function descriptions (which are just mapping objects with special keys) and returns only json-serializable results. In the future, it will probably use `marshal` module and will be able to operate exactly like `map` function (accept function objects and return any objects).

That this is an early alpha version, so stuff may brake / change quicky!
