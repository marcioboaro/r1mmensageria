from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class MS14Simplified(BaseModel):
    Codigo_de_MSG : str
    ID_do_Solicitante : str
    ID_Rede_Lockers: int
