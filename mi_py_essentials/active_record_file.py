
from typing import Union, Optional
import json, os, logging
# pip
import yaml
import aiofiles
import aiofiles.os

from .active_record import ActiveRecord

class ActiveRecordFile(ActiveRecord):
    def __init__(self, storage_dir: str, id:Optional[ Union[str, int] ] = None, file_extension: str = ".json"):
        self._id = id
        self._storage_dir = storage_dir
        self._file_ext = file_extension.lower()
        if self._file_ext not in [".json", ".yaml"]:
            raise ValueError("Unsupported file extension. Use '.json' or '.yaml'")

    def create( self, id:Union[str, int] ) -> "ActiveRecord":
        return ActiveRecordFile( self._storage_dir, id, self._file_ext )
    
    async def load(self, default_data:dict={} ) -> dict:
        if self._id is None or await aiofiles.os.path.exists( self._file_path() ) == False:
            return default_data
        
        file_path = self._file_path()
        async with aiofiles.open(file_path, mode='r') as file:            
            logging.info(f'Loading {file_path}')
            content = await file.read()
            if self._file_ext == ".json":
                return json.loads(content)
            elif self._file_ext == ".yaml":
                return yaml.safe_load(content)
        
    async def save(self, data: dict) -> Union[str, int]:
        content = ""
        if self._file_ext == ".json":
            content = json.dumps(data, indent=4)
        elif self._file_ext == ".yaml":
            content = yaml.safe_dump(data, default_flow_style=False)
        
        # gen new id
        if self._id is None:
            entries = await aiofiles.os.scandir(self._storage_dir)
            self._id = len( list(entries) ) + 1
            while await aiofiles.os.path.exists( self._file_path () ):
                self._id += 1            
                
        # create parent dir
        file_path = self._file_path()
        dir = os.path.dirname( file_path )
        await aiofiles.os.makedirs( dir, exist_ok=True )
        
        # write it
        async with aiofiles.open(file_path, mode='w') as file:
            logging.info(f'Writing to {file_path}')
            await file.write(content)
            
        return self._id
    
    def _file_path( self ) -> str:
        return self._storage_dir + "/" + str( self._id ) + self._file_ext