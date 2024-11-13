import argparse
import inspect
from typing import Callable, Dict, Any, Optional, List, get_origin, get_args

class CmdProxy:
    def __init__(self, description="undefined"):
        self._functions: Dict[str, Callable] = {}
        self._description = description

    def add_function(self, func: Callable, name:Optional[str]=None) -> "CmdProxy":
        name = name or func.__name__
        assert name not in self._functions, f'Function "{name}" must not already be added, got function "{self._functions[name]}"'
        """Add a function to the command proxy."""
        self._functions[name] = func
        return self

    def remove_function(self, func_name: str) -> bool:
        """Remove a function from the command proxy by name."""
        if func_name in self._functions:
            del self._functions[func_name]
            return True
        return False

    def exec(self, args: Optional[list] = None) -> Any:
        """Execute a function by parsing arguments based on the function's type hints."""
        parser = argparse.ArgumentParser(description=self._description)
        parser.add_argument("function_name", choices=self._functions.keys(), help="The function to execute")

        # Parse the function name first to know which function to add args for
        partial_args, _ = parser.parse_known_args(args)
        func_name = partial_args.function_name
        func = self._functions[func_name]

        # Build a new parser for function arguments
        func_parser = argparse.ArgumentParser(description=f"{func_name}")
        func_parser.add_argument("function_name", choices=[func_name], help=func_name)
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            # Determine argument type and default value
            arg_type = param.annotation if param.annotation != param.empty else str
            is_positional = param.default == param.empty
            default_value = None if is_positional else param.default
            # Handle boolean types with default True or False using store actions
            def str2bool(value):
                return str(value).lower() in [ 'true', 't', 'yes', 'y', '1' ]
            if arg_type is bool:
                arg_type = str2bool
            # Handle list types
            nargs = None
            if get_origin(arg_type) is list:
                arg_type = get_args(arg_type)[0]  # Get the type inside the list, e.g., `int` in `List[int]`
                nargs = "+"
                
            func_parser.add_argument(
                name if is_positional else f"--{name}",
                type=arg_type,
                default=default_value,
                nargs=nargs,                    
                help=f"{arg_type.__name__} argument"
            )

        # Parse function-specific arguments
        func_args = func_parser.parse_args(args)
        func_kwargs = vars(func_args)

        # Call the function with parsed arguments, excluding 'function_name'
        func_kwargs.pop("function_name", None)
        return func(**func_kwargs)

