from typing import Optional
from pydantic import BaseModel



class LC59(BaseModel):
   CD_MSG: str
   idRede: int
   idLocker: str