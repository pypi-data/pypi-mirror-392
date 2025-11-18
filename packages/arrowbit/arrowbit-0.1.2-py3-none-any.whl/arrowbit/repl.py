import os

# Runtime elements
from .ext.runtime import Runtime, Environment
from .ext.runtime import on_error, on_start
from .ext.core import command_registry

# Data, objects & variables
from .ext.parser import Object

# Errors
from .ext import errors

# ==================================================================================

from . import VERSION
from .ext import parser


def execute(cmd: parser.Command | str, strict: bool = True) -> Object | None:
    if isinstance(cmd, str):
        cmd = parser.parse_cmd(cmd)

    temp_env = Environment(strict)
    temp_runtime = Runtime()

    temp_runtime.execute(cmd, temp_env)

    return temp_env.result


RUNTIME = Runtime()
ENV = Environment(strict = True)

def run():
    @on_start()
    def rt_start(env: Environment):
        os.system('cls' if os.name == 'nt' else 'clear')
        if env.strict: print("\033[1;33m[STRICT MODE]\033[0m", end = ' ')
        print(f"ArrowBit v{VERSION} - REPL")
        print()

    @on_error()
    def rt_error(env: Environment, err: errors.Error):
        if isinstance(err, errors.UserCancel):
            print("UserCancel caught, leaving REPL")
        else:
            print(f'\033[31m{err.title}:\033[0m {err.message}')

    # ================

    if 'on_start' in command_registry:
        callback = command_registry['on_start']
        _on_start = callback["function"]
        _on_start(ENV)


    try:
        while True:
            cmd = input("> ")
            RUNTIME.execute(cmd, ENV)

    except KeyboardInterrupt as e:
        print()

        if 'on_error' in command_registry:
            cmd = command_registry['on_error']
            _on_error = cmd["function"]
            return _on_error(ENV, errors.UserCancel())
        else:
            raise e

    except errors.Error as e:
        print()

        if 'on_error' in command_registry:
            cmd = command_registry['on_error']
            _on_error = cmd["function"]
            return _on_error(ENV, e)
        else:
            raise e