from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class Encomendas(BaseModel):
    ID_Encomenda: str
    Tipo_de_Servico_Reserva: str
    Etiqueta_Encomenda_Rede1minuto: str

class MS21(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    ID_da_Estacao_do_Locker: str
    Codigo_Resposta_MS21: str
    Data_Hora_Resposta: datetime
    ID_Transacao_Unica: str
    Info_Encomendas: list[Encomendas]
    Versao_Mensageria: str
