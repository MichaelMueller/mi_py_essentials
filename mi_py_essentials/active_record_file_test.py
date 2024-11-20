
from typing import Coroutine, Union, Any, Optional
import json, os, tempfile, asyncio, shutil, logging
# pip

from mi_py_essentials import AbstractTest, ActiveRecordFile

class ActiveRecordFileTest(AbstractTest):
    def __init__(self) -> None:
        super().__init__()
        
    async def _exec(self) -> None:
        tmp_dir = await self.tmp_dir()

        active_record_file = ActiveRecordFile( tmp_dir )        
        data = { "int": 1, "float": 2.2, "bool": False, "str": "string" }
        
        id_ = await active_record_file.save(data)        
        data_copy = await active_record_file.load( id_ )        
        
        self._print(f'json.dumps(data): {json.dumps(data)}')
        self._print(f'json.dumps(data_copy): {json.dumps(data_copy)}')
        
        self._assert( json.dumps(data) == json.dumps(data_copy), "loading and saving works" )
        self._print(f'id(data): {id(data)}')
        self._print(f'id(data_copy): {id(data_copy)}')
        self._assert( id(data) != id(data_copy), "calling save() and load() should create copies of the data" )
                
    
    