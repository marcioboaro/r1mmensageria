from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class MS17(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    Codigo_Resposta_MS17: str
    Data_Hora_Resposta: datetime
    ID_da_Estacao_do_Locker:str
    ID_da_Porta_do_Locker: str
    ID_Transacao_Unica: str
    DataHora_Inicio_Reserva: datetime
    DataHora_Final_Reserva: datetime
    Versao_Mensageria: Optional[str]


