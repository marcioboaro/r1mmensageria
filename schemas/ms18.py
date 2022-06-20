from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time


class MS18(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    Data_Hora_Solicitacao: datetime
    ID_da_Estacao_do_Locker: str
    Categoria_Porta: str
    Geração_de_QRCODE_na_Resposta_MS19: str
    DataHora_Inicio_Locacao: datetime
    DataHora_Final_Locacao: datetime
    Versao_Mensageria: str




