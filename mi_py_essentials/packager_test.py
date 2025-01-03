# built-in
import asyncio, aiofiles
import aiofiles.os
# local
from .test import Test
from .async_utils import AsyncUtils
from .venv_creator_test import VenvCreatorTest
from .packager import Packager

class PackagerTest(Test):
    def __init__(self, parent:"Test") -> None:
        super().__init__(parent)
        
    async def _exec(self) -> None:
        if await VenvCreatorTest(self).exec() == False:
            return False
        
        tmp_dir = await self.tmp_dir()
        req_file = tmp_dir + "/requirements.txt"
        await AsyncUtils().write( req_file, "pyjokes" )
        temp_dir_path = tmp_dir + "/dist"
        output_zip=temp_dir_path + "/test.zip"
        p = Packager( Packager.Args( output_zip=output_zip, requirements_file=req_file, minpy=(3, 8), additional_files={req_file: "requirements.txt"} ) )
        await p.exec()
        
        self._check( await aiofiles.os.path.exists(output_zip ), f'file exists( "{output_zip}" )' )