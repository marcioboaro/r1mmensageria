from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class MS09(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    Data_Hora_Solicitacao: datetime
    Tipo_de_servico_abertura_porta: int
    ID_Transacao_Unica: str
    ID_Encomenda: Optional[str]
    Geracao_de_QRCODE_na_Resposta_MS06: str
    Geracao_de_Codigo_de_Abertura_de_Porta_na_Resposta_MS06:str
    Versao_Mensageria: Optional[str]




  