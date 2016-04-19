# convenient-rpc

It's a project that allows to call functions on many remote machines (workers). Basically, you specify args, function, module name (and package, if needed), it installs it and imports modules on all the workers, passes args to the function and gives you your result.

You'll have to install wrapper as a python module, launch `task_server` at one machine and launch `task_process` at all the workers. Sounds complicated, but I will supply Docker images for it, so deploying such a thing on AWS (or any other hoster that supports Docker) will be pretty simple.

Then you will be able to use it like this:

    from wrapper import API

    api = API('mytaskserver.somedomain')
    
    function_description = {
        "package": "my_package",
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
        print(result)

Note that this is an early alpha version, so stuff may brake / change quicky.
