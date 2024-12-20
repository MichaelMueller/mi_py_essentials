
from typing import Union, Any, Optional
import json, os
# pip

from mi_py_essentials import Test, InMemoryActiveRecord

class InMemoryActiveRecordTest(Test):
    def __init__(self, parent:"Test") -> None:
        super().__init__(parent)
        
    async def _exec(self) -> None:
        
        in_memory_active_record = InMemoryActiveRecord()        
        data = { "int": 1, "float": 2.2, "bool": False, "str": "string" }
        
        id_ = await in_memory_active_record.save(data)        
        data_copy = await in_memory_active_record.load( id_ )        
        
        self._check( json.dumps(data) == json.dumps(data_copy), "loading and saving works" )
        self._print(f'id(data): {id(data)}')
        self._print(f'id(data_copy): {id(data_copy)}')
        self._check( id(data) != id(data_copy), "calling save() and load() should create copies of the data" )
        
        
        
        
        
    