from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class LC18(BaseModel):
   CD_MSG: Optional [str]
   idRede: Optional [int]
   idLocker: Optional [str]
   DT: datetime
   CD_NovaVersao: Optional [str]
   URL_CD_Nova_Versao: Optional[str]
   DT_TrocaVersao: datetime
   URL_Script_Instalacao: Optional[str]
   Longitude: Optional[str]
   Latitude: Optional[str]
   VersaoSoftware: Optional[str]
   VersaoMensageria: Optional [str]

