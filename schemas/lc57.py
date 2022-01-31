from typing import Optional
from pydantic import BaseModel


class Content(BaseModel):
   idRede: int
   idLocker: str

class LC57(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None