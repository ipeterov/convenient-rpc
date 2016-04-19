# convenient-rpc

It's a project that allows to call functions on many remote machines (workers). Basically, you specify args, function, module name (and package, if needed), it installs it and imports modules on all the workers, passes args to the function and gives you your result. 


## task-server

This is the part that manages the nodes and exposes a convinient REST API to manage tasks. It also collects basic function runtime stats and tries to predict how much processing time you need.

API looks like that:

    /user/
        Public API that will be exposed to users. Will require authentification soon (if you don't want everybody to use your workers).
    
        submit_task POST JSON
            Example input:
                {
                    "package": "my_package",
                    "function": "foo",
                    "args": (42, 1),
                    "kwargs": {
                        "bar": true,
                        "spam": false
                    }
                }
            Returns:
                {
                    "sucsess": <bool>,
                    "id": <id of the new task>
                }
            Comment:
                You must specify the `function` argument, others are optional.
        
        request_answer/<id> GET
            Returns:
                {
                    "sucsess": <bool>,
                    "answer": <answer that some worker made>
                }
            Comment:
                `id` is the one you get from the output of "/submit_task"

        estimate_time_left GET
            Returns:
                {
                    "sucsess": <bool>,
                    "time": <float>
                }
            Comment:
                `time` is in seconds that are needed to finish current task queue with one (average) processing core
    
    /worker/
        These are methods that only workers should use. Will require authentification soon. 
    
        request_task GET
            Returns:
                {
                    "sucsess": <bool>,
                    "id": <some id>,
                    "task": <>
                }
    
        submit_answer POST
            Example input:
                {
                    "id": <id of the computed task>,
                    "answer": <stuff you want to return>
                }
            Returns:
                {
                    "sucsess": <bool>,
                }

## task-processor

This is the part that should be run on all the workers.

To be able to use custom packages (which is the point of this project), you can specify your custom PyPi repo in the [.pypirc] file and workers will automatically use it.

It should be run from a virtualenv with dependencies from `requirements.txt` installed.

You can just launch it with `env_path/python3 node.py` or import it (to specify control server and stuff like that)  and run like this:

    from node import TaskProcessor, process_task

    processor = TaskProcessor()
    processor.mainloop()

You can also redefine `process_task` to do custom stuff with your tasks. Your variant should accept a tuple like this one: `(id_, function, args, kwargs)` and return a tuple like this: `(id_, result)`.

[.pypirc]: https://docs.python.org/2/distutils/packageindex.html#pypirc
