from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class MS01(BaseModel):
    Codigo_de_MSG: str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    Codigo_Resposta_MS04: Optional[str]
    Data_Hora_Solicitacao: Optional[datetime]
    Codigo_Pais_Locker: Optional[str]
    Cidade_Locker: Optional[str]
    Cep_Locker: Optional[str]
    Bairro_Locker: Optional[str]
    Endereco_Locker: Optional[str]
    Numero_Locker: Optional[str]
    Complemento_Locker: Optional[str]
    Modelo_Uso_Locker: Optional[int]
    Categoria_Locker: Optional[int]
    Tipo_Armazenamento: Optional[int]
    Codigo_Dimensao_Portas_Locker: Optional[int]
    Modelo_Operacao_Locker: Optional[int]
    ID_da_Estacao_do_Locker: Optional[str]
    LatLong: Optional[str]
    Versao_Mensageria: Optional[str]
