
from typing import Union, Any, Optional
import json, os
# pip
import yaml
import aiofiles
import aiofiles.os

from .active_record import ActiveRecord

class InMemoryActiveRecord(ActiveRecord):
    
    def __init__(self, id:Optional[ Union[str, int] ] = None ):
        self._id = id

    def create( self, id:Optional[ Union[str, int] ] = None ) -> "ActiveRecord":
        return InMemoryActiveRecord( id )
    
    async def load(self, default_data:dict={} ) -> dict:
        if self._id is None or self._id not in self._data:
            return default_data
        
        return InMemoryActiveRecord._data[self._id]
        
    async def save(self, data: dict) -> Union[str, int]:
        # gen new id
        data_copy = json.loads( json.dumps(data) )
        if self._id is None:
            num_entries = len( InMemoryActiveRecord._data )
            self._id = num_entries
            while self._id in InMemoryActiveRecord._data:
                self._id += 1            
        InMemoryActiveRecord._data[self._id] = data_copy
        return self._id
        
    _data = {} # static memory