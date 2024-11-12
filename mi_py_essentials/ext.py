# built-in
import typing, inspect
from typing import get_type_hints, Union, get_origin, get_args, Any, TypedDict, Optional
import argparse, sys, json, traceback

# local
import mi_py_essentials.core as core 
  
class Api(core.Api):
    
    def __init__(self) -> None:
        super().__init__()        
        self.add_function( ObjectToSchema(self) )
        self.add_function( ExecCommandLine(self) )
        
    async def object_to_schema( self, obj:Any ) -> dict:
        return await self.exec( inspect.currentframe().f_code.co_name, locals() ) 
      
    async def exec_command_line( self, command_line_args:list[str]=sys.argv ) -> dict:
        return await self.exec( core.camel_to_snake( ExecCommandLine.__name__ ), locals() )          

class ObjectToSchemaArgs(TypedDict):
    obj: Any

class ObjectToSchema(core.Function):      
    
    def __init__(self, api: Api) -> None:
        super().__init__(api)
        
    async def exec( self, args:ObjectToSchemaArgs ) -> dict:
        return self._object_to_schema( args["obj"] )
       
  # internal
    def _python_type_to_json_type(self, python_type):
        if python_type in {int, float}:
            return "number"
        elif python_type == str:
            return "string"
        elif python_type == bool:
            return "boolean"
        elif python_type == list:
            return "array"
        elif python_type == dict:
            return "object"
        elif get_origin(python_type) == list:
            return "array"
        elif get_origin(python_type) == dict:
            return "object"
        else:
            raise ValueError(f"Unsupported Python type: {python_type}")

    def _python_type_to_json_schema(self, python_type):
        schema = {}
        origin = get_origin(python_type)
        if origin == Union:
            args = get_args(python_type)
            if int in args and float in args: # int and float will result in anyOf number, number -> remove int
                args = tuple(x for x in args if x != int)
            elif type(None) in args:
                args = tuple(x for x in args if x != type(None))
                
            # Handle Optional type (i.e., Union with None)
            if len(args) == 1:
                return self._python_type_to_json_schema(args[0])
            else:
                schema["anyOf"] = [self._python_type_to_json_schema(arg) for arg in args]
                return schema

        elif origin == list:
            item_type = get_args(python_type)[0] if get_args(python_type) else None
            schema["type"] = "array"
            if item_type:
                schema["items"] = self._python_type_to_json_schema(item_type)
            return schema

        elif origin == dict:
            key_type, value_type = get_args(python_type)
            if key_type != str:
                raise ValueError("Only string keys are allowed in JSON objects")
            schema["type"] = "object"
            schema["additionalProperties"] = self._python_type_to_json_schema(value_type)
            return schema

        elif python_type in [int, float, str, bool]:
            schema["type"] = self._python_type_to_json_type(python_type)
            return schema

        elif origin == typing.Literal:
            literals = list(get_args( python_type ))
            any_of_literals = []
            literal_types = []
            for literal in literals:
                literal_type = type(literal)
                if not literal_type in literal_types:
                    literal_types.append( literal_type )
                 
                literal_def = self._python_type_to_json_schema(literal_type)
                literal_def["enum"] = [ literal ]
                any_of_literals.append( literal_def )
            
            if len( literal_types ) == 1:                
                schema["type"] = "string"
                schema["enum"] = list(get_args( python_type ))
            else:         
                schema["anyOf"] = any_of_literals                
            # todo mixed types
            return schema            

        else:
            raise ValueError(f"Unsupported Python type: {python_type}")

    def _object_to_schema(self, obj):
        schema = { "$schema": "http://json-schema.org/draft-07/schema#" }
        if not hasattr(obj, "__annotations__"):            
            schema["type"] = self._python_type_to_json_schema( obj )
            return schema

        else:
            schema.update( {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            } )

            type_hints = get_type_hints(obj)

            for key, hint in type_hints.items():
                schema["properties"][key] = self._python_type_to_json_schema(hint)
                schema["required"].append(key)

        return schema
            
class ExecCommandLineArgs(TypedDict):
    command_line_args:list[str]
    
class ExecCommandLine( core.Function ):
    
    def __init__(self, api: Api) -> None:
        super().__init__(api)
        
    async def exec(self, args:Optional[ExecCommandLineArgs]=None ) -> Union[None, Any]:
        
        # initial function_name parsing
        parser = argparse.ArgumentParser(description=self.api().name())
        function_names = self.api().shell_function_names()
        parser.add_argument("function_name", type=str, choices=function_names, help="The name of the function to execute")
        cmd_args = args["command_line_args"] if args != None else sys.argv
        if len(cmd_args) > 0 and cmd_args[0] == sys.argv[0]:
            cmd_args = cmd_args[1:]
        parsed_args, _ = parser.parse_known_args( args=cmd_args )        
        function_name:str = parsed_args.function_name
        f:core.ShellFunction = self.api().function( function_name )
        
        # reconfigure argparser with shell function
        parser = argparse.ArgumentParser(description=f"Arguments for {function_name}")
        parser.add_argument("function_name", type=str, choices=[function_name], help=f.help())
        schema = await f.args_json_schema()
        properties:dict = schema.get("properties", {})
        required = schema.get("required", [])

        for prop, prop_schema in properties.items():
            arg_type = str  # Default to string if type is not recognized
            choices = None
            
            allowed_types = ["integer", "boolean", "number", "string"]
            assert "type" in prop_schema and prop_schema["type"] in allowed_types, f'Argument "{prop}" schema must contain type within: {allowed_types}, got {prop_schema}'
            
            if prop_schema["type"] == "integer":
                arg_type = int
            elif prop_schema["type"] == "boolean":
                arg_type = lambda x: (str(x).lower() == 'true')  # Convert to boolean
            elif prop_schema["type"] == "number":
                arg_type = float
            elif prop_schema["type"] == "string":
                arg_type = str               
                if "enum" in prop_schema:
                    choices = prop_schema["enum"]     
            else:
                raise ValueError(f'Unsupported type {prop_schema["type"]}')
            
            if prop in required:
                parser.add_argument(f"{prop}", type=arg_type, choices=choices, help=f"{prop} ({prop_schema['type']})")        
            else:
                parser.add_argument(f"--{prop}", type=arg_type, choices=choices, help=f"{prop} ({prop_schema['type']})")        
        
        # parse the cmd_args and run the function
        parsed_args = parser.parse_args( args=cmd_args )        
        return await f.exec( vars(parsed_args) )
    
  
class ShellFunction(core.ShellFunction):
    def __init__(self, api: Api) -> None:
        super().__init__(api)
           
    def api(self) -> Api:
        return super().api()
    
    async def args_json_schema(self) -> None | dict:
        return await self.api().object_to_schema( list(get_type_hints(self.exec).values())[0] )
    
    async def result_json_schema(self) -> None | dict:
        return await self.api().object_to_schema( get_type_hints(self.exec).get("return") )