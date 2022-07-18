from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Content(BaseModel):
   idRede: int
   idLocker: str

class LC23(BaseModel):
   CD_MSG: str
   content: Optional[Content] = None
