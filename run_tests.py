# built-ing
import os
import sys
import asyncio
# local
import mi_py_essentials.tests
                
if __name__ == "__main__":
    sys.path.append( os.path.realpath( os.path.dirname(__file__) + "/" + mi_py_essentials.__name__) )
    tests_ok = asyncio.run( mi_py_essentials.tests.run() )
    sys.exit( 0 if tests_ok else 1 )