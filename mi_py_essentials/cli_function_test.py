# built-in
import asyncio
# local
from .test import Test
from .cli_function import CliFunction

class CliFunctionTest(Test):
    def __init__(self, parent:"Test") -> None:
        super().__init__(parent)
        
    async def _exec(self) -> None:
        
        def add( op1:float, op2:float ) -> float:
            return op1+op2
        
        async def heavy_add( op1:float, op2:float ) -> float:
            asyncio.sleep(0.1)
            return op1+op2
        
        two_plus_two_point_one = await CliFunction( add, ["1.0", "2.1"] ).exec()
        self._check( two_plus_two_point_one == 3.1, f'two_plus_two_point_one == 3.1, got {two_plus_two_point_one}')