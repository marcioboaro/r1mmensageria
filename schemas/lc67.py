from typing import Optional
from pydantic import BaseModel



class LC67(BaseModel):
   Codigo_de_MSG: str
   idRede: int
   idLocker: str