from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class Encomendas(BaseModel):
    ID_Encomenda: str
    Tipo_de_Servico_Reserva: str

class MS20(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    ID_da_Estacao_do_Locker: str
    ID_PSL_Designado: str
    Info_Encomendas: list[Encomendas]
    Versao_Mensageria: str

