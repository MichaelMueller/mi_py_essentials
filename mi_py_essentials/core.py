import typing
from typing import get_type_hints, Union, get_origin, get_args, Any, TypedDict, get_type_hints
import traceback
    
# interfaces
class Function:    
    def __init__(self, api:"Api") -> None:
        self._api = api
    
    def api(self) -> "Api":
        return self._api
    
    async def exec( self, args:Union[None, dict] ) -> Union[None, Any]:
        raise NotImplementedError()    
    
    def name(self) -> str:        
        return self.__class__.__name__
            
class ShellFunction(Function):  
    def __init__(self, api:"Api") -> None:
        super().__init__(api)
    
    # from function
    async def exec( self, args:Union[None, dict] ) -> Union[None, Any]:
        raise NotImplementedError()    
        
    def help( self ) -> Union[None, dict]:
        return self.name()
      
    async def args_json_schema( self ) -> Union[None, dict]:
        raise NotImplementedError()   
    
    async def result_json_schema( self ) -> Union[None, dict]:
        raise NotImplementedError()   
    
    
class Api:           
    def __init__(self) -> None:
        self._functions:dict[str, Function] = {}
        self._shell_functions:dict[str, ShellFunction] = {}
    
    def name(self) -> str:        
        return self.__class__.__name__
    
    def add_function( self, f:Function ) -> "Api":
        f_with_same_name = self.function( f.name() )
        assert f_with_same_name == None, f'Functon name "{f.name()}" must be unique but is already used by {f_with_same_name.__class__.__name__} class'
    
        self._functions[f.name()] = f
        
        if isinstance( f, ShellFunction ):
            self._shell_functions[f.name()] = f
        return self
    
    def function_names(self) -> list[str]:
        return self._functions.keys()
    
    def shell_function_names(self) -> list[str]:
        return self._shell_functions.keys()
    
    def function( self, name:str ) -> Union[Function, None]:
        return self._functions[name] if name in self._functions else None
     
    def remove_function( self, name:str ) -> "Api":
        assert name in self._shell_functions, f'Function "{name}" must exist to be removed'
        del self._functions[name]
        if name in self._shell_functions:
            del self._shell_functions[name]
        return self
        
    async def exec( self, function_name:str, args:Union[None, dict] ) -> Union[None, Any]:
        f = self.function( function_name )
        assert f != None, f'Function "{function_name}" must exist to be executed'
        return await f.exec( args )
    
class Test (ShellFunction):
    
    def __init__(self, api: Api) -> None:
        super().__init__(api)
            
    def dependent_tests(self) -> list["Test"]:
        return []
    
    def name(self) -> str:        
        raise NotImplementedError()   
      
    def args_json_schema( self ) -> Union[None, dict]:
        raise NotImplementedError()   
    
    def result_json_schema( self ) -> Union[None, dict]:
        raise NotImplementedError()   
    
    async def exec(self, _=None ) -> bool:
        print( f'****** {self.__class__.__name__} - STARTING' )
        for t in self.dependent_tests():
            if not await t.exec():
                print( f'****** {self.__class__.__name__} - FAILED dependent test {t.__class__.__name__}' )
                return False                
        try:
            await self._tidy_up_if_needed()
            await self._exec()            
            await self._tidy_up_if_needed()
            print( f'****** {self.__class__.__name__} - PASSED' )            
            return True
        except Exception as e:
            # Catch all exceptions and print the stack trace
            traceback.print_exc()
            print( f'****** {self.__class__.__name__} - FAILED with exception (see trace above)' )
            return False

    async def _tidy_up_if_needed(self) -> None:
        pass

    async def _exec(self):
        raise NotImplementedError()
        
    def _assert( self, condition:bool, assertion_description:str ) -> None:
        if not condition:
            raise AssertionError( f'{assertion_description}' )
        else:
            print(f'****** {self.__class__.__name__} - PASSED assertion {assertion_description} ')

    def _check( self, condition:bool, check_description:str ):
        if not condition:
            print( f'****** {self.__class__.__name__} - FAILED check {check_description}' )
        else:
            print(f'****** {self.__class__.__name__} - PASSED check {check_description}')

    def _expect_exception( self, func:callable, func_description:str, exception_class:type ) -> None:
        unexcepted_exception = None
        
        try:
            func()        
        except Exception as e:
            if isinstance(e, exception_class):                
                print(f'****** {self.__class__.__name__} - PASSED expect exception {exception_class.__name__} when calling {func_description}')
            else:
                unexcepted_exception = e
        
        if unexcepted_exception is not None:
            raise unexcepted_exception
        
    def _print(self, msg):
        print( f'****** {self.__class__.__name__} - {msg}' )
        
