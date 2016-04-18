# task-processor

It's a part of my project that allows to call functions on many remote machines (workers). Basically, you specify args, function, module name (and package, if needed), it installs it and imports modules on all the workers, passes args to the function and gives you your result. This is the part that should be run on all the workers.

To be able to use custom packages (which is the point of this project), you can specify your custom PyPi repo in the [.pypirc] file and workers will automatically use it.

It should be run from a virtualenv with dependencies from `requirements.txt` installed.

You can just launch it with `env_path/python3 node.py` or import it (to specify control server and stuff like that)  and run like this:

    from node import TaskProcessor, process_task

    processor = TaskProcessor()
    processor.mainloop()

You can also redefine `process_task` to do custom stuff with your tasks. Your variant should accept a tuple like this one: `(id_, function, args, kwargs)` and return a tuple like this: `(id_, result)`.

[.pypirc]: https://docs.python.org/2/distutils/packageindex.html#pypirc
