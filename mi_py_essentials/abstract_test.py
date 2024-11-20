from typing import Any
import tempfile, asyncio, traceback, shutil

from mi_py_essentials import Test

class AbstractTest (Test):
    def __init__(self) -> None:
        super().__init__()
        self._tmp_dir = None
        
    async def _exec(self) -> None:
        raise NotImplementedError()
    
    async def tmp_dir(self) -> str:
        if not self._tmp_dir:    
            loop = asyncio.get_event_loop()
            # Run the synchronous tempfile.mkdtemp in a thread pool to make it non-blocking
            self._tmp_dir = await loop.run_in_executor(None, tempfile.mkdtemp)
            self._print(f'Created tmp dir "{self._tmp_dir}"')
        return self._tmp_dir
    
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
            print( f'****** {self.__class__.__name__} - FAILED with exception' )
            return False
    
    async def _tidy_up_if_needed(self) -> None:
        if self._tmp_dir:
            loop = asyncio.get_event_loop()            
            self._print(f'Deleting tmp dir "{self._tmp_dir}"')
            await loop.run_in_executor(None, lambda: shutil.rmtree(self._tmp_dir))
            
    def _assert( self, condition:bool, assertion_description:str ) -> None:
        if not condition:
            raise AssertionError( f'{assertion_description}' )
        else:
            print(f'****** {self.__class__.__name__} - Assertion PASSED: {assertion_description} ')
    
    def _check( self, condition:bool, check_description:str ):
        if not condition:
            print( f'****** {self.__class__.__name__} - Check FAILED: {check_description}' )
        else:
            print(f'****** {self.__class__.__name__} - Check PASSED: {check_description}')
    
    def _expect_exception( self, func:callable, func_description:str, exception_class:type ) -> None:
        unexcepted_exception = None
        
        try:
            func()        
        except Exception as e:
            if isinstance(e, exception_class):                
                print(f'****** {self.__class__.__name__} - Expected exception PASSED: {exception_class.__name__} when {func_description}')
            else:
                unexcepted_exception = e
        
        if unexcepted_exception is not None:
            raise unexcepted_exception
        
    def _print(self, msg):
        print( f'****** {self.__class__.__name__} - {msg}' )
        