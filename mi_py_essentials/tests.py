import sys, asyncio, os, logging
from typing import Callable, Dict, Any, Optional, List, get_origin, get_args

# local
sys.path.insert( 0, os.path.dirname( os.path.dirname( __file__ ) ) )
from mi_py_essentials import Test, AbstractTest, InMemoryActiveRecordTest, ActiveRecordFileTest, CmdProxyTest, InteractiveCmdProxyTest

class Tests(AbstractTest):
    def __init__(self) -> None:
        super().__init__()
                
    async def exec(self) -> bool:   
        logging.basicConfig(
            level=logging.DEBUG,  # Set the logging level
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Define log message format
            handlers=[
                logging.StreamHandler()  # Output log messages to console
            ])
        tests_passed = await super().exec() 
        sys.exit( 0 if tests_passed else 1 )
        
    def dependent_tests(self) -> list[Test]:
        return [ InMemoryActiveRecordTest(), ActiveRecordFileTest(), CmdProxyTest(), InteractiveCmdProxyTest() ]
    
    async def _exec(self) -> None:
        pass

if __name__ == "__main__":
    asyncio.run( Tests().exec() )