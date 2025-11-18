from functools import wraps
from inspect import signature

from .core import command_registry

def define_command(name: str):
	def decorator(func):
		sig = signature(func)

		command_registry[name] = {
			"function": func,
			"signature": sig,
		}

		@wraps(func)
		def wrapper(*args, **kwargs):
			return func(*args, **kwargs)

		return wrapper

	return decorator

command = define_command