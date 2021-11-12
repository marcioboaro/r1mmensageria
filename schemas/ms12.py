from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class pod(BaseModel):
    ID_Encomenda: str
    Codigo_Conformidade_POD: str
    Conteudo_POD: str

class MS12(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    ID_Transacao_Unica: str
    ID_da_Estacao_do_Locker: str
    ID_do_Operador_do_Locker: str
    ID_da_Porta_do_Locker: str
    Data_Hora_POD: datetime
    Dados_POD: list[pod]
    Versao_Mensageria: str
