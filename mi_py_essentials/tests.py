import sys, asyncio, os, logging
from typing import Callable, Dict, Any, Optional, List, get_origin, get_args
# local
from .test import Test
from .cli_app_test import CliAppTest
from .active_record_file_test import ActiveRecordFileTest
from .in_memory_active_record_test import InMemoryActiveRecordTest
from .cli_function_test import CliFunctionTest
from .interactive_cli_function_test import InteractiveCliFunctionTest

class Tests(Test):
    def __init__(self) -> None:
        super().__init__(None)
                   
    def name( self ) -> str:
        package_name = os.path.basename( os.path.dirname(__file__) )
        
        return f"{package_name}.{self.__class__.__name__}"
        
    async def _exec(self) -> bool:
        return await InMemoryActiveRecordTest(self).exec() \
            and await ActiveRecordFileTest(self).exec() \
            and await CliAppTest(self).exec() \
            and await CliFunctionTest(self).exec()\
            and await InteractiveCliFunctionTest(self).exec()