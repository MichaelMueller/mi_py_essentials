
from typing import Coroutine, Union, Any, Optional
import json, os, tempfile, asyncio, shutil, logging
# pip

from mi_py_essentials import Test, CmdApp

class CmdAppTest(Test):
    def __init__(self, parent:"Test") -> None:
        super().__init__(parent)
        
    async def _exec(self) -> None:
        cmd_proxy = CmdApp()
        
        self._print(f'CmdProxyTest.add.__name__: {CmdAppTest.add.__name__}')
        cmd_proxy.add_function( CmdAppTest.add )
        self._check( cmd_proxy.remove_function( "does_not_exist" ) == False, "Removal of non existing function should return False" )
        self._check( cmd_proxy.remove_function( CmdAppTest.add.__name__ ) == True, "Removal of existing function should return True" )
        
        cmd_proxy.add_function( CmdAppTest.add )
        await self._expect_exception( lambda: cmd_proxy.add_function( CmdAppTest.add ), "adding a function with the same name", AssertionError)
                
        self._print(f'self.string_concat.__name__: {self.string_concat.__name__}')
        cmd_proxy.add_function( self.and_, "and" )        
        cmd_proxy.add_function( self.string_concat )
        cmd_proxy.add_function( self.join )
        
        self._check( cmd_proxy.exec( ["add", "1", "1"] ) == 2, f"calling add 1 1 should return 2" )
        self._check( cmd_proxy.exec( ["and", "1", "--bool_op2", "0"] ) == False, f"calling and 0 1 should return False" )        
        res = cmd_proxy.exec( ["string_concat", "0", "--str2", "1"] )
        self._check( res == "01", f"calling string_concat 0 1 should return 01, got {res}" )
                
        res = cmd_proxy.exec( ["join", "0", "1", "2"] )
        self._check( res == "0,1,2", f"calling join 0 1 2 should return 0,1,2, got {res}" )
        
    def add( addend1:float, addend2:int ) -> float:
        return addend1 + addend2
    
    def and_( self, bool_op1:bool, bool_op2:bool=True ) -> bool:
        return bool(bool_op1) and bool_op2
        
    def string_concat( self, str1:str, str2:str="str2" ) -> bool:
        return str1 + str2
    
    def join( self, strings:list[str] ) -> str:
        return ",".join( strings )
        
        
    
    