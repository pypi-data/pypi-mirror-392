"""
# Handsoff

Automatic file transferer with SCP Unix command.

# Commands

## In Code
```python
import handsoff
handsoff.set(host="127.0.0.0", user="MovingJu", ...)
handsoff.push("./handsoff.py", "~/")
```

## In CLI
```
handsoff set --host 127.0.0.0 --user MovingJu
handsoff push --file ./handsoff.py --target ~/
```
"""

from .modules.Commands_generate import Commands_generate
from .modules.side_effects import run_command_, read_dotenv_
import inspect
import os

# handlers

_command_handler = Commands_generate()

def set(host: str, user: str, client: str, server: str = "", pem: str = "", **params: str):
    """
    - host: IP or something to which you want to transfer.
    - user: name of userspace your files go.
    - file: unlimited number of files you want to transfer, enumerate its names.
    - target: target path where you want to transfer.
    """
    parameters: dict[str, str] = {
        "host": host,
        "user": user,
        "client": client,
        "server": server,
        "pem": pem,
    }
    for key, val in params.items():
        parameters[key] = val
    _command_handler.set_parameters_(parameters)
def push(*file: str, target: str = ""):
    command = _command_handler.push(
        file, target
    )
    caller_file = inspect.stack()[1].filename
    caller_dir = os.path.dirname(os.path.abspath(caller_file))
    print(f"dir test : {caller_dir}")
    run_command_(command, cwd=caller_dir)
def pull(*file: str, target: str = ""):
    command = _command_handler.pull(
        file, target
    )
    caller_file = inspect.stack()[1].filename
    caller_dir = os.path.dirname(os.path.abspath(caller_file))
    run_command_(command, cwd=caller_dir)
    return
def get():
    return _command_handler.get_parameters()