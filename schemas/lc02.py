from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Content(BaseModel):
   idReferencia: str
   idSolicitante: int
   idRede: str
   idTransacaoUnica: str
   idLocker: str
   idLockerPorta: str
   DT: datetime
   VersaoSoftware: str
   VersaoMensageria: str

class LC02(BaseModel):
   CD_MSG: str
   content: Optional[Content] = None




