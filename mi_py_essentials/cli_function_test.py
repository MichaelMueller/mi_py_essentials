# built-in
from typing import Literal, Optional
import asyncio
# pip
import pydantic
# local
from .test import Test
from .cli_function import CliFunction
from .async_utils import AsyncUtils

class CliFunctionTest(Test):
    def __init__(self, parent:"Test") -> None:
        super().__init__(parent)
        
    async def _exec(self) -> None:
        
        def add( op1:float, op2:float ) -> float:
            return op1+op2
        
        async def heavy_add( op1:float, op2:float ) -> float:
            await asyncio.sleep(0.1)
            return op1+op2
        
        two_plus_two_point_one = await CliFunction( add, ["1.0", "2.1"] ).exec()
        self._check( two_plus_two_point_one == 3.1, f'two_plus_two_point_one == 3.1, got {two_plus_two_point_one}')
        
        async_two_plus_two_point_one = await CliFunction( heavy_add, ["1.0", "2.1"] ).exec()
        self._check( async_two_plus_two_point_one == 3.1, f'async_two_plus_two_point_one == 3.1, got {async_two_plus_two_point_one}')

        
        class CalcArgs(pydantic.BaseModel):
            op1:int
            op2:int
            operator:Literal["+","-"]

        def calc( args:CalcArgs ) -> int:
            if args.operator == "+":    return args.op1 + args.op2
            else:                       return args.op1 - args.op2
            
        args = CalcArgs(op1=2, op2=2, operator="+")
        two_plus_two_with_pydantic_model = await CliFunction( calc, [args.model_dump_json()] ).exec()
        self._check( two_plus_two_with_pydantic_model == 4, f'two_plus_two_with_pydantic_model == 4, got {two_plus_two_with_pydantic_model}')

        # testing args from file
        tmp_file = ( await self.tmp_dir() ) + "/calc_args.json"
        self._print(f'writing to json file "{tmp_file}"')
        await AsyncUtils.write_json( tmp_file, args.model_dump() )
        two_plus_two_with_pydantic_model = await CliFunction( calc, [args.model_dump_json()] ).exec()
        self._check( two_plus_two_with_pydantic_model == 4, f'two_plus_two_with_pydantic_model == 4, got {two_plus_two_with_pydantic_model}')

        # testing optional params
        def calc( op1:float, op2:float, operator:Optional[str]="+" ) -> float:
            if operator == "+":    return op1 + op2
            else:                       return op1 - op2
        
        two_plus_two_with_optional_param = await CliFunction( calc, ["2.0", "2.0"] ).exec()
        self._check( two_plus_two_with_optional_param == 4, f'two_plus_two_with_optional_param == 4, got {two_plus_two_with_optional_param}')

        # testing literal param
        def calc( op1:float, op2:float, operator:Literal["+", "-"]="+" ) -> float:
            if operator == "+":    return op1 + op2
            else:                       return op1 - op2
        
        two_minuts_two_with_literal_param = await CliFunction( calc, ["2.0", "2.0", "--operator", "-"] ).exec()
        self._check( two_minuts_two_with_literal_param == 0, f'two_minuts_two_with_literal_param == 0, got {two_minuts_two_with_literal_param}')
        