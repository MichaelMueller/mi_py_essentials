import sys, asyncio, os, logging
from typing import Callable, Dict, Any, Optional, List, get_origin, get_args

# local
parent_dir = os.path.dirname( __file__ )
# module_name = os.path.splitext(os.path.basename(__file__))[0]
package_dir = os.path.dirname( parent_dir )
if not package_dir in sys.path:
    sys.path.insert( 0, os.path.dirname( os.path.dirname( __file__ ) ) )
    
package_name = os.path.basename( parent_dir )
__package__ = package_name

from mi_py_essentials import Test, InMemoryActiveRecordTest, ActiveRecordFileTest, CliAppTest
from .cli_function_test import CliFunctionTest
from .interactive_cli_function_test import InteractiveCliFunctionTest

class Tests(Test):
    def __init__(self) -> None:
        super().__init__(None)
                   
    def name( self ) -> str:
        return f"{package_name}.{self.__class__.__name__}"
        
    async def _exec(self) -> bool:
        return await InMemoryActiveRecordTest(self).exec() \
            and await ActiveRecordFileTest(self).exec() \
            and await CliAppTest(self).exec() \
            and await CliFunctionTest(self).exec()\
            and await InteractiveCliFunctionTest(self).exec()

if __name__ == "__main__":
    asyncio.run( Tests.exec() )