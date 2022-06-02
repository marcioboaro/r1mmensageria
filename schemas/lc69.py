from typing import Optional
from pydantic import BaseModel

class LC69(BaseModel):
   CD_MSG: str
   idRede: int
   idLocker: str