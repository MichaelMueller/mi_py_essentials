from typing import Any, Callable, Awaitable, get_origin, get_args
import argparse, logging, inspect
# pip
import aioconsole
# local
from .function import Function

class InteractiveCliFunction(Function):
    
    def __init__(self, func:callable):
        super().__init__()
        self._func = func
        self._input_func:Callable[[str], Awaitable[str] ] = aioconsole.ainput
               
    async def exec(self) -> Any:
        func:callable = self._func
        desc = inspect.getdoc( func )
        func_name = func.__name__

        print(f'Executing "{func_name}" interactively')
        if desc:
            print(f'Description: {desc}')

        sig = inspect.signature(func)
        func_kwargs = {}

        # Collect arguments interactively
        for name, param in sig.parameters.items():
            arg_type = param.annotation if param.annotation != param.empty else str
            is_required = param.default == param.empty

            # Prompt for the argument value
            while True:
                try:
                    raw_input = await self._input_func(
                        f"Enter value for '{name}' ({arg_type.__name__})"
                        + (f" [default={param.default}]" if not is_required else "")
                        + ": "
                    )
                    raw_input = raw_input.strip()

                    # Handle default values
                    if not raw_input and not is_required:
                        func_kwargs[name] = param.default
                        break

                    # Convert the input to the expected type
                    if get_origin(arg_type) is list:
                        item_type = get_args(arg_type)[0]
                        func_kwargs[name] = [item_type(i) for i in raw_input.split()]
                    elif arg_type is bool:
                        func_kwargs[name] = raw_input.lower() in ["true", "t", "yes", "y", "1"]
                    else:
                        func_kwargs[name] = arg_type(raw_input)
                    break
                except ValueError:
                    print(f"Invalid value for '{name}'. Expected type: {arg_type.__name__}.")

        # Execute the function with collected arguments
        result = await func(**func_kwargs) if inspect.iscoroutinefunction(func) else func(**func_kwargs)
        #print(f"Result: {result}")
        return result