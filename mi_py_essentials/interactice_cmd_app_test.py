
from typing import Coroutine, Union, Any, Optional
import json, os, tempfile, asyncio, shutil, logging, sys
# pip

from mi_py_essentials import Test, InteractiveCmdApp

class InteractiveCmdAppTest(Test):
    def __init__(self, parent:"Test") -> None:
        super().__init__(parent)
        
    async def _exec(self) -> None:
        in_cmd_proxy = InteractiveCmdApp()
        
        self._print(f'InteractiveCmdProxyTest.add.__name__: {InteractiveCmdAppTest.add.__name__}')
        in_cmd_proxy.add_function( InteractiveCmdAppTest.add )
        self._check( in_cmd_proxy.remove_function( "does_not_exist" ) == False, "Removal of non existing function should return False" )
        self._check( in_cmd_proxy.remove_function( InteractiveCmdAppTest.add.__name__ ) == True, "Removal of existing function should return True" )
        
        in_cmd_proxy.add_function( InteractiveCmdAppTest.add )
        await self._expect_exception( lambda: in_cmd_proxy.add_function( InteractiveCmdAppTest.add ), "adding a function with the same name", AssertionError)
                
        self._print(f'self.string_concat.__name__: {self.string_concat.__name__}')
        in_cmd_proxy.add_function( self.and_, "and" )        
        in_cmd_proxy.add_function( self.string_concat )
        in_cmd_proxy.add_function( self.join )
        
        input_return_values = ["add", "1", "1", "1", "0", "string_concat", "0", "1", "join", "0 1 2"]
        def test_input_func(msg:str) -> Any:
            sys.stdout.write(msg)
            arg = input_return_values.pop(0)
            print(arg)
            return arg
        in_cmd_proxy._input_func = test_input_func        
        
        self._check( await in_cmd_proxy.exec() == 2, f"calling add 1 1 should return 2" )
        self._check( await in_cmd_proxy.exec( "and" ) == False, f"calling and 0 1 should return False" )        
        res = await in_cmd_proxy.exec()
        self._check( res == "01", f"calling string_concat 0 1 should return 01, got {res}" )
                
        res = await in_cmd_proxy.exec()
        self._check( res == "0,1,2", f"calling join 0 1 2 should return 0,1,2, got {res}" )
        
    def add( addend1:float, addend2:int ) -> float:
        return addend1 + addend2
    
    def and_( self, bool_op1:bool, bool_op2:bool=True ) -> bool:
        return bool(bool_op1) and bool_op2
        
    def string_concat( self, str1:str, str2:str="str2" ) -> bool:
        return str1 + str2
    
    def join( self, strings:list[str] ) -> str:
        return ",".join( strings )
        
        
    
    