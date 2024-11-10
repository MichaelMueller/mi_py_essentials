from typing import Union, Any

from dataclasses import dataclass
from dataclasses_json import dataclass_json

import mi_py_essentials.interface as interface
import mi_py_essentials.abstract as abstract
import mi_py_essentials.impl as impl

# global run method
async def run() -> bool:
    api = impl.Api()
    api.add_function( HelloWorldFunction() )
    api.add_function( HelloWorldShellFunction() )

    print( f'api.function_names(): {api.function_names()}')
    print( f'api.shell_function_names(): {api.shell_function_names()}')

    print( f'api.exec("hello_world", args=None): { await api.exec("hello_world", args=None) }')
    print( 'api.exec("api.exec("hello_world_shell_function", args=\{"name": "Michi"}): ' + f'{ await api.exec("hello_world_shell_function", args={"name": "Michi"}) }')

# test class implementations
class HelloWorldFunction(interface.Function):

    async def exec(self, api:interface.Api, args:Union[None, dict, interface.DataObject]):
        print("Hello World")

    def name(self):
        return "hello_world"

@dataclass_json
@dataclass
class HelloWorldShellFunctionArgs(interface.DataObject):
    name: str

class HelloWorldShellFunction(interface.ShellFunction):

    def create_data_object_from_args( self, args:dict ) -> interface.DataObject:
        return HelloWorldShellFunctionArgs.from_dict(args)

    async def exec( self, api:interface.Api, args:HelloWorldShellFunctionArgs ):
        print(f"Hello World {args.name}")

    def name(self):
        return "hello_world"

# test classes