from typing import Union, Any

import interface
    
class Api(interface.Api):           
    
    def __init__(self) -> None:
        self._functions:dict[str, interface.Function] = []
        self._shell_functions:dict[str, interface.ShellFunction] = []
    
    def add_function( self, f:interface.Function ) -> bool:
        if f.name() in self._functions:
            return False
        self._functions[f.name()] = f
        
        if hasattr(f, "create_data_object_from_args") and callable(getattr(f, "create_data_object_from_args")):
            self._shell_functions[f.name()] = f
        return True
    
    def function_names(self) -> list[str]:
        return self._functions.keys()
    
    def shell_function_names(self) -> list[str]:
        return self._functions.keys()
    
    def function( self, name:str ) -> Union[interface.Function, None]:
        return self._functions[name] if name in self._functions else None
     
    def remove_function( self, name:str ):
        if name in self._shell_functions:
            del self._functions[name]
            if name in self._shell_functions:
                del self._shell_functions[name]
            return True
        return False
        
    async def exec( self, function_name:str, args:Union[None, dict, interface.DataObject] ) -> Union[None, Any]:
        raise NotImplementedError()