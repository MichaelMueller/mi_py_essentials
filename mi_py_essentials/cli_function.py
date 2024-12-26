from typing import Any, Callable, get_origin, get_args, Annotated, Union, Literal
import argparse, logging, inspect, json
from pathlib import Path
# pip
import pydantic
from pydantic import BaseModel, ValidationError
# local
from .function import Function

class CliFunction(Function):
    
    def __init__(self, func:callable, args:list[str]|None=None, parser_cb:Callable[[argparse.ArgumentParser], None]|None=None):
        super().__init__()
        self._func = func
        self._args = args
        self._parser_cb = parser_cb
               
    async def exec(self) -> Any:
        func:callable = self._func
        desc = inspect.getdoc( func )
        """Execute a function by parsing arguments based on the function's type hints."""
        parser = argparse.ArgumentParser(description=desc)
        if self._parser_cb != None:
            self._parser_cb( parser )
                    
        # Build a new parser for function arguments
        sig = inspect.signature(func)
        known_args:list[str] = []
        for name, param in sig.parameters.items():
            # Determine argument type and default value
            arg_type = param.annotation if param.annotation != param.empty else str
            is_positional = param.default == param.empty
            default_value = None if is_positional else param.default
            # Handle list types
            nargs = None
            choices=None

            # Handle boolean types with default True or False using store actions
            def str2bool(value):
                return str(value).lower() in [ 'true', '1' ]
                
            if arg_type is bool:
                arg_type = str2bool
            elif get_origin(arg_type) is list:
                arg_type = get_args(arg_type)[0]  # Get the type inside the list, e.g., `int` in `List[int]`
                nargs = "+"
            elif get_origin(arg_type) == Annotated:
                arg_type = get_args(arg_type)[0]
            elif get_origin(arg_type) == Union:
                arg_type = CliFunction.argparse_union_type( get_args(arg_type) )                
            elif isinstance(arg_type, type) and issubclass( arg_type, pydantic.BaseModel ):
                arg_type = CliFunction.validate_model_input( arg_type )
            elif get_origin(arg_type) == Literal:
                choices = list( get_args(arg_type)) 
                arg_type = type( get_args(arg_type)[0] )
                
            parser.add_argument(
                name if is_positional else f"--{name}",
                type=arg_type,
                default=default_value,
                nargs=nargs,                    
                help=f"{arg_type.__name__} argument",
                choices=choices
            )
            known_args.append(name)

        # Parse function-specific arguments
        func_args = parser.parse_args() if self._args is None else parser.parse_args( self._args )
        func_kwargs = vars(func_args)
        known_kwargs = {}
        for key in func_kwargs.keys():
            if key in known_args:
                known_kwargs[key] = func_kwargs[key]

        # Call the function with parsed arguments, excluding 'function_name'
        return await func(**known_kwargs) if inspect.iscoroutinefunction(func) else func(**known_kwargs)
    
    def validate_model_input(model_class: BaseModel):
        def validator(input_str: str):
            # Check if the input is a valid file path
            if Path(input_str).is_file():
                try:
                    with open(input_str, 'r') as file:
                        data = json.load(file)
                except (OSError, json.JSONDecodeError) as e:
                    raise argparse.ArgumentTypeError(f"Error reading JSON from file '{input_str}': {e}")
            else:
                try:
                    data = json.loads(input_str)
                except json.JSONDecodeError as e:
                    raise argparse.ArgumentTypeError(f"Input string is not valid JSON: {e}")

            # Validate data against the Pydantic model
            try:
                return model_class(**data)
            except ValidationError as e:
                raise argparse.ArgumentTypeError(
                    f"Input data does not match {model_class.__name__} schema:\n{e}\n"
                    f"Expected schema:\n{model_class.schema_json(indent=2)}"
                )

        return validator
    
    def argparse_union_type(valid_types):
        def mixed_type(value: str) -> Union[str, int, float, None]:
            """
            Validate and parse the input value into one of the types specified in valid_types.
            """
            # Check for None explicitly
            if value.lower() in ("none", "null", "nil"):
                if None in valid_types:
                    return None
                raise ValueError(f"None is not allowed as a value for this argument.")

            # Try to parse as each type in valid_types
            for valid_type in valid_types:
                try:
                    if valid_type is bool and value.lower() in [ 'true', 'false', '1', '0' ]:
                        return value.lower() in [ 'true', '1' ]
                    if valid_type is int:
                        return int(value)
                    if valid_type is float:
                        return float(value)
                    if valid_type is str:
                        return value
                except ValueError:
                    continue

            raise ValueError(f"Value '{value}' is not valid for types {valid_types}.")
        return mixed_type

