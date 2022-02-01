from typing import Optional
from pydantic import BaseModel


class Content(BaseModel):
   idRede: int
   idLocker: str

class LC55(BaseModel):
   Codigo_de_MSG: str
   idRede: int
   idLocker: str