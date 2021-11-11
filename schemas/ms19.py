from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time


class MS19(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    ID_da_Estacao_do_Locker: str
    ID_da_Porta_do_Locker: str
    Codigo_Resposta_MS19: str
    Data_Hora_Resposta: datetime
    Codigo_Pais_Locker: str
    Cidade_Locker: str
    CEP_Locker: str
    Bairro_Locker: str
    Endereco_Locker: str
    Numero_Locker: str
    Complemento_Locker: str
    LatLong: str
    Categoria_Locker: str
    Modelo_Operacao_Locker: str
    Categoria_Porta: str
    ID_Transacao_Unica: str
    ID_Geracao_QRCODE: str
    DataHora_Inicio_Locacao: datetime
    DataHora_Final_Locacao: datetime
    Versao_Mensageria: str

