from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class MS10(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    Codigo_Resposta_MS10: str
    ID_Transacao_Unica: str
    ID_Encomenda: str
    ID_Geracao_QRCODE: str
    Geracao_de_Codigo_para_Abertura_Porta: str
    Data_Hora_Resposta: datetime
    Versao_Mensageria: Optional[str]


