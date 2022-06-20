from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class Encomendas(BaseModel):
    ID_Encomenda: Optional[str] = None
    Tipo_de_Servico_Reserva: Optional[int] = None

class MS20(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    Data_Hora_Solicitacao: datetime
    ID_da_Estacao_Locker: str
    ID_PSL_Designado: str
    ID_Transacao_Unica: str
    Info_Encomendas: list[Encomendas]
    Versao_Mensageria: str
