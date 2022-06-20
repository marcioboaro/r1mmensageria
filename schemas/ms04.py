from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class PortaLocker(BaseModel):
    ID_da_Porta_do_Locker: str
    idlockerportafisica: int
    Categoria_Porta: str
    Modelo_Uso_Porta: str
    Codigo_Dimensao_Portas_Locker: str
    Comprimento_Porta: int
    Largura_Porta: int
    Altura_Porta: int
    Peso_Maximo_Porta: int
    Moeda_Faturamento: Optional[str] = None
    Preço_da_Tarifa_Uso_Porta: Optional[int] = None

class Locker(BaseModel):
    Codigo_Pais_Locker: str
    Cidade_Locker: str
    CEP_Locker: str
    Bairro_Locker: str
    Endereco_Locker: str
    Numero_Locker: str
    Complemento_Locker: str
    Modelo_uso_Locker: str
    Categoria_Locker: str
    Tipo_Armazenamento: str
    Modelo_Operacao_Locker: str
    Nome_Fantasia_do_Locker: str
    ID_da_Estacao_do_Locker: str
    LatLong: str
    Portas: Optional[PortaLocker] = None

class MS04(BaseModel):
    Codigo_de_MSG: str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    Codigo_Resposta_MS04: Optional[str] = None
    Data_Hora_Resposta: Optional[datetime]
    Estacao_Locker: Optional[Locker] = None
    Versao_Mensageria: str
 
 