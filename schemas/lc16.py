from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class LC16(BaseModel):
   CD_MSG: Optional [str]
   idRede: Optional [int]
   IdLocker: Optional [str]
   DT: Optional [str]
   VersaoMensageria: Optional [str]
