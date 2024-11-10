from typing import Any
import logging
import traceback

from .Test import Test

class AbstractTest (Test):
    def __init__(self) -> None:
        super().__init__()
        
    def dependent_tests(self) -> list[Test]:
        return []
        
    async def exec(self) -> bool:        
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
        