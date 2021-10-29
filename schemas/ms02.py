from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

# MS02

class Locker(BaseModel):
    Codigo_Pais_Locker: str
    Cidade_Locker: str
    Cep_Locker: str
    Bairro_Locker: str
    Endereco_Locker: str
    Numero_Locker: str
    Complemento_Locker: str
    Modelo_Uso_Locker: str
    Categoria_Locker: str
    Tipo_Armazenamento: Optional[str] = None
    Modelo_Operacao_Locker: Optional[str] = None
    Nome_Fantasia_do_locker: str
    ID_da_estacao_do_locker: str
    LatLong: str
    Segunda_Hora_Inicio: Optional[str] = None
    Segunda_Hora_Fim: Optional[str] = None
    Terca_Hora_Inicio: Optional[str] = None
    Terca_Hora_Fim: Optional[str] = None
    Quarta_Hora_Inicio: Optional[str] = None
    Quarta_Hora_Fim: Optional[str] = None
    Quinta_Hora_Inicio: Optional[str] = None
    Quinta_Hora_Fim: Optional[str] = None
    Sexta_Hora_Inicio: Optional[str] = None
    Sexta_Hora_Fim: Optional[str] = None
    Sabado_Hora_Inicio: Optional[str] = None
    Sabado_Hora_Fim: Optional[str] = None
    Domingo_Hora_Inicio: Optional[str] = None
    Domingo_Hora_Fim: Optional[str] = None
    Feriados_Hora_Inicio: Optional[str] = None
    Feriados_Hora_Fim: Optional[str] = None

class MS02(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    Data_Hora_Resposta: datetime
    Estacao_Locker: list[Locker]
