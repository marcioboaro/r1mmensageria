from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class LC16(BaseModel):
   CD_MSG: Optional [str]
   idRede: Optional [int]
   idLocker: Optional [str]
   DT: Optional [str]
   VersaoSoftware: Optional[str]
   VersaoMensageria: Optional [str]
