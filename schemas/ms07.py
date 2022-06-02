from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class MS07(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    Data_Hora_Solicitacao: Optional[datetime]
    ID_Transacao_Unica: str
    Comentario_Cancelamento_Reserva: Optional[str]
    Versao_Mensageria: Optional[str]


