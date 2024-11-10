# built-ing
import os
import sys
import asyncio
# local
from mi_py_essentials.SelfTestSuite import SelfTestSuite
        
async def main() -> bool:        
    return await SelfTestSuite().exec()    
        
if __name__ == "__main__":
    tests_ok = asyncio.run(main())
    sys.exit( 0 if tests_ok else 1 )