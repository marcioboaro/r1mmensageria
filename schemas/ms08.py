from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time


class MS08(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    Codigo_Resposta_MS08: str
    Data_Hora_Resposta: datetime
    ID_Transacao_Unica: str
    Versao_Mensageria: str

  