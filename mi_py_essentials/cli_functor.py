from typing import Any
from .functor import Functor

class CliFunctor(Functor):
    
    def __init__(self):
        super().__init__()
               
    def exec(self) -> Any:
        raise NotImplementedError()