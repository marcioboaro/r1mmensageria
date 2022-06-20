from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time


class MS16(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    Data_Hora_Solicitacao: datetime
    ID_da_Estacao_do_Locker:str
    ID_da_Porta_do_Locker: str
    ID_Transacao_Unica: str
    DataHora_Inicio_Reserva: Optional[datetime]
    DataHora_Final_Reserva: Optional[datetime]
    Versao_Mensageria: Optional[str]


