# built-in
import asyncio, aiofiles
import aiofiles.os
# local
from .test import Test
from .async_utils import AsyncUtils
from .venv_creator import VenvCreator
from .code_runner_test import CodeRunner, CodeRunnerTest

class VenvCreatorTest(Test):
    def __init__(self, parent:"Test") -> None:
        super().__init__(parent)
        
    async def _exec(self) -> None:
        if await CodeRunnerTest(self).exec() == False:
            return False
        
        tmp_dir = await self.tmp_dir()
        
        await AsyncUtils().write( tmp_dir + "/requirements.txt", "pyjokes" )
        
        venv_dir = tmp_dir + "/.venv"
        
        c = VenvCreator( VenvCreator.Args( venv_path=venv_dir, requirements_file=tmp_dir + "/requirements.txt" ) )
        await c.exec()
        
        # check if the venv was created correctly   
        venv_dir_exists = await aiofiles.os.path.exists( venv_dir )
        self._check( venv_dir_exists==True, f'venv_dir_exists==True' )
        
        _,stderr_text,returnCode = await CodeRunner( CodeRunner.Args(code_or_script_path=f"import pyjokes", venv_path=venv_dir)).exec()
        
        self._check( returnCode==0, f"returnCode==0, got {returnCode} with err={stderr_text}" )