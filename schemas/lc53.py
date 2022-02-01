from typing import Optional
from pydantic import BaseModel


class LC53(BaseModel):
   Codigo_de_MSG: str
   idRede: int
   idLocker: str