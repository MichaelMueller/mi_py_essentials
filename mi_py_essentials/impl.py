from typing import Union, Any
import logging
import mi_py_essentials.interface as interface
    
class Api(interface.Api):           
    
    def __init__(self) -> None:
        self._functions:dict[str, interface.Function] = {}
        self._shell_functions:dict[str, interface.ShellFunction] = {}
    
    def add_function( self, f:interface.Function ) -> "Api":
        f_with_same_name = self.function( f.name() )
        assert f_with_same_name == None, f'Functon name "{f.name()}" must be unique but is already used by {f_with_same_name.__class__.__name__} class'
    
        self._functions[f.name()] = f
        
        if self._is_shell_function( f ):
            self._shell_functions[f.name()] = f
        return self
    
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
        f = self.function( function_name )

        if self._is_shell_function( f ):
            f:interface.ShellFunction = f
            args = f.create_data_object_from_args( args )

        return await f.exec( self, args )
    
    def _is_shell_function( self, f:interface.Function ) -> bool:
        return hasattr(f, "create_data_object_from_args") and callable(getattr(f, "create_data_object_from_args"))