import argparse, logging
import inspect
from typing import Callable, Dict, Any, Optional, List, get_origin, get_args

from .log import Log
from .function import Function
from .cli_function import CliFunction

class CliApp(Function):
    def __init__(self, description:str|None=None, args:list[str]|None=None):
        self._functions: Dict[str, Callable] = {}
        self._description = description
        self._args = args

    def set_args( self, args:list[str] ) -> "CliApp":
        self._args = args
        return self

    def add_function(self, func: callable, name:Optional[str]=None) -> "CliApp":
        name = name or func.__name__
        assert name not in self._functions, f'Function "{name}" must not already be added, got function "{self._functions[name]}"'
        logging.debug(f'inserting function "{name}"')
        """Add a function to the command proxy."""
        self._functions[name] = func
        return self

    def remove_function(self, func_name: str) -> bool:
        """Remove a function from the command proxy by name."""
        if func_name in self._functions:
            del self._functions[func_name]
            return True
        return False

    async def exec(self) -> Any:
        """Execute a function by parsing arguments based on the function's type hints."""
        parser = argparse.ArgumentParser(description=self._description)
        self._setup_std_args( parser, self._functions.keys(), "The name of the function to be executed")

        partial_args, _ = parser.parse_known_args() if self._args == None else parser.parse_known_args(self._args)
                
        # Set up basic logging
        Log.setup( partial_args.log_level, partial_args.log_filter )
            
        # Parse the function name first to know which function to add args for
        func_name = partial_args.function_name
        func = self._functions[func_name]
        def parser_cb( parser:argparse.ArgumentParser ):
            self._setup_std_args(parser, [ func_name ], func_name)        
        return await CliFunction(func, args=self._args, parser_cb=parser_cb).exec()

    def _setup_std_args( self, parser:argparse.ArgumentParser, funcs:list[str], func_help ) -> None:
        parser.add_argument("function_name", choices=funcs, help=func_help)
        parser.add_argument("-l", "--log_level", type=str, choices=["notset", "debug", "info", "warn", "error"], default="info", help="The basic log level")
        parser.add_argument("-lf", "--log_filter", type=str, default=None, help="An optional regex that removes matching log lines")
