from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class MS11(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    ID_Transacao_Unica: str
    ID_do_Remetente_Notificacao: str
    ID_do_Destinatario_Notificacao: str
    Tipo_de_Servico_Reserva: int
    Status_Reserva_Anterior: int
    Status_Reserva_Atual: int
    Data_Hora_Notificacao_Evento_Reserva: Optional[datetime]
    Versao_Mensageria: Optional[str]
