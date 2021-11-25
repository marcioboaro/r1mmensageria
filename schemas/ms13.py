from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class MS13(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    ID_do_Remetente_Notificacao: str
    ID_do_Destinatario_Notificacao: str
    ID_Transacao_Unica: str
    Tipo_de_Servico_Reserva: int
    ID_Encomenda: str
    Status_Encomenda_Anterior: int
    Status_Encomenda_Atual: int
    Data_Hora_Notificacao_Evento_Encomenda: Optional[datetime]
    Versao_Mensageria: Optional[str]

