from typing import Any, Callable, get_origin, get_args
import argparse, logging, inspect
# local
from .function import Function

class CliFunction(Function):
    
    def __init__(self, func:callable, args:list[str]|None=None):
        super().__init__()
        self._func = func
        self._args = args
               
    async def exec(self) -> Any:
        func:callable = self._func
        desc = inspect.getdoc( func )
        func_name = func.__name__
        """Execute a function by parsing arguments based on the function's type hints."""
        parser = argparse.ArgumentParser(description=desc)
        parser.add_argument("function_name", choices=[func_name], help=func_name)        
        
        # Build a new parser for function arguments
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
                
            parser.add_argument(
                name if is_positional else f"--{name}",
                type=arg_type,
                default=default_value,
                nargs=nargs,                    
                help=f"{arg_type.__name__} argument"
            )

        # Parse function-specific arguments
        func_args = parser.parse_args() if self._args is None else parser.parse_args( self._args )
        func_kwargs = vars(func_args)

        # Call the function with parsed arguments, excluding 'function_name'
        func_kwargs.pop("function_name", None)
        return await func(**func_kwargs) if inspect.iscoroutinefunction(func) else func(**func_kwargs)