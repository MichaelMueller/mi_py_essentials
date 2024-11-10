from typing import Union, Any

class Test:    
    async def exec(self) -> bool:
        raise NotImplementedError()
                
                
class DataObject:        
    async def to_json( self ) -> str:
        raise NotImplementedError()
    
    async def json_schema( self ) -> dict:
        raise NotImplementedError()
    
    
class Function:    
    async def exec( self, api:"Api", args:Union[None, dict, DataObject] ) -> Union[None, Any]:
        raise NotImplementedError()    
    
    def name(self) -> str:        
        raise NotImplementedError()    
    
        
class ShellFunction:    
    def create_data_object_from_args( self, args:dict ) -> DataObject:
        raise NotImplementedError()
    
    async def exec( self, api:"Api", args:Union[None, DataObject] ) -> Union[None, DataObject]:
        raise NotImplementedError()
    
    
class Api:           
            
    def function_names(self) -> list[str]:
        raise NotImplementedError()
    
    def shell_function_names(self) -> list[str]:
        raise NotImplementedError()
    
    def function( self, name:str ) -> Union[Function, None]:
        raise NotImplementedError()

    async def exec( self, function_name:str, args:Union[None, dict, DataObject] ) -> Union[None, Any]:
        raise NotImplementedError()