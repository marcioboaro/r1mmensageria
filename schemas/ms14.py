from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class MS14(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante_Designado : str
    ID_Rede_Lockers: int
    ID_do_Solicitante_Designador: str
    Data_Hora_Solicitacao: Optional[datetime]
    DataHora_Inicio_Consuta_Encomendas_Designadas: Optional[datetime]
    DataHora_Final_Consuta_Encomendas_Designadas: Optional[datetime]
    Codigo_Pais_Locker:  Optional[str]
    Cidade_Locker:  Optional[str]
    ID_TICKET_Ocorrencia_Encomenda: Optional[str]
    Versao_Mensageria: Optional[str]

