import inspect
from typing import Callable, Dict, Any, Optional, List, get_origin, get_args

class InteractiveCmdProxy:
    def __init__(self, description="undefined"):
        self._functions: Dict[str, Callable] = {}
        self._description = description
        self._input_func = input

    def add_function(self, func: Callable, name: Optional[str] = None) -> "InteractiveCmdProxy":
        name = name or func.__name__
        assert name not in self._functions, f'Function "{name}" already exists.'
        self._functions[name] = func
        return self

    def remove_function(self, func_name: str) -> bool:
        if func_name in self._functions:
            del self._functions[func_name]
            return True
        return False

    async def exec(self, func_name:Optional[str]=None):
        if not self._functions:
            print("No functions have been added.")
            return

        # List available functions
        if not func_name:
            print("Available functions:")
            for name in self._functions:
                print(f" - {name}")
            
            # Prompt user to select a function
            func_name = self._input_func("Enter the name of the function to execute: ").strip()
        if func_name not in self._functions:
            print(f"Function '{func_name}' does not exist.")
            return

        func = self._functions[func_name]
        sig = inspect.signature(func)
        func_kwargs = {}

        # Collect arguments interactively
        for name, param in sig.parameters.items():
            arg_type = param.annotation if param.annotation != param.empty else str
            is_required = param.default == param.empty

            # Prompt for the argument value
            while True:
                try:
                    raw_input = self._input_func(
                        f"Enter value for '{name}' ({arg_type.__name__})"
                        + (f" [default={param.default}]" if not is_required else "")
                        + ": "
                    ).strip()

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
