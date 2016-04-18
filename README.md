# task-server

It's a part of my project that allows to call functions on many remote machines (workers). Basically, you specify args, function, module name (and package, if needed), it installs it and imports modules on all the workers, passes args to the function and gives you your result. This is the part that manages the nodes and exposes a convinient REST API to manage tasks. It also collects basic function runtime stats and tries to predict how much processing time you need.

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
                You must specify the "function" argument, others are optional.
        
        request_answer/<id> GET
            Returns:
                {
                    "sucsess": <bool>,
                    "answer": <answer that some worker made>
                }
            Comment:
                "id" is the one you get from the output of "/submit_task"
    
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
