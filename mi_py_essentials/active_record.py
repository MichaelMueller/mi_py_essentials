from typing import Callable, Dict, Any, Optional, List, get_origin, get_args, Union

class ActiveRecord:
    def create( self, id:Optional[ Union[str, int] ] = None ) -> "ActiveRecord":
        raise NotImplementedError()
    
    async def load( self, default_data:dict={} ) -> dict:
        raise NotImplementedError()
    
    async def save( self, data:dict ) -> Union[str, int]:
        raise NotImplementedError()