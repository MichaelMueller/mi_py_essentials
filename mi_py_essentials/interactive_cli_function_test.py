# built-in
import asyncio, sys
# local
from .test import Test
from .interactive_cli_function import InteractiveCliFunction

class InteractiveCliFunctionTest(Test):
    def __init__(self, parent:"Test") -> None:
        super().__init__(parent)
        
    async def _exec(self) -> None:
        
        # custom input function
        input_return_values = ["1", "1", "1", "0", "0", "1", "0 1 2"]
        async def test_input_func(msg:str) -> str:
            sys.stdout.write(msg)
            arg = input_return_values.pop(0)
            print(arg)
            return arg
        
        icli = InteractiveCliFunction(self.add)
        icli._input_func = test_input_func
        
        self._check( await icli.exec() == 2, f"calling add 1 1 should return 2" )
        
        icli = InteractiveCliFunction(self.and_)
        icli._input_func = test_input_func
        self._check( await icli.exec() == False, f"calling and 0 1 should return False" )        
        
        icli = InteractiveCliFunction(self.string_concat)
        icli._input_func = test_input_func
        res = await icli.exec()
        self._check( res == "01", f"calling string_concat 0 1 should return 01, got {res}" )
                
        icli = InteractiveCliFunction(self.join)
        icli._input_func = test_input_func
        res = await icli.exec()
        self._check( res == "0,1,2", f"calling join 0 1 2 should return 0,1,2, got {res}" )
        
    def add( self, addend1:float, addend2:int ) -> float:
        return addend1 + addend2
    
    def and_( self, bool_op1:bool, bool_op2:bool=True ) -> bool:
        return bool(bool_op1) and bool_op2
        
    def string_concat( self, str1:str, str2:str="str2" ) -> bool:
        return str1 + str2
    
    def join( self, strings:list[str] ) -> str:
        return ",".join( strings )
        