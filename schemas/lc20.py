from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Cancelamento de Reserva
class LC20(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

class Content(BaseModel):
   ID_Referencia: str
   ID_Solicitante: str
   idRede: int
   idTransacao: str
   idLocker: str
   idLockerPorta: str
   Versao_Software: str
   Versao_Mensageria: int

# Resposta de Canecelamento de Reserva
class LC21(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

class Content(BaseModel):
   Codigo_de_MSG_Resposta: str
   ID_Referencia: str
   ID_Solicitante: str
   idRede: int
   idTransacao: str
   idLocker: str
   idLockerPorta: str
   Versao_Software: str
   Versao_Mensageria: int

# Prorrogação de Reserva
class LC22(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

class Content(BaseModel):
   ID_Referencia: str
   ID_Solicitante: str
   idRede: int
   idTransacao: str
   idLocker: str
   idLockerPorta: str
   DT_InicioReservaLocacao: datetime
   DT_finalReservaLocacao: datetime
   Versao_Software: str
   Versao_Mensageria: int

# Resposta Prorrogação de Reserva
class LC23(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

class Content(BaseModel):
   Codigo_de_MSG_Resposta: str
   ID_Referencia: str
   ID_Solicitante: str
   idRede: int
   idTransacao: str
   idLocker: str
   idLockerPorta: str
   DT_InicioReservaLocacao: datetime
   DT_finalReservaLocacao: datetime
   Versao_Software: str
   Versao_Mensageria: int

# Locação de Porta
class LC24(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

class Content(BaseModel):
   ID_Referencia: str
   ID_Solicitante: str
   idRede: int
   idTransacao: str
   Tipo_de_Servico_Reserva: int
   idLocker: str
   idLockerPorta: str
   QRCODE: str
   CD_PortaAbertura: str
   DT_InicioReservaLocacao: datetime
   DT_finalReservaLocacao: datetime
   Versao_Software: str
   Versao_Mensageria: int

# Resposta de Locação de Porta
class LC25(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

class Content(BaseModel):
   Codigo_de_MSG_Resposta: str
   ID_Referencia: str
   ID_Solicitante: str
   idRede: int
   idTransacao: str
   Tipo_de_Servico_Reserva: int
   idLocker: str
   idLockerPorta: str
   QRCODE: str
   CD_PortaAbertura: str
   DT_InicioReservaLocacao: datetime
   DT_finalReservaLocacao: datetime
   Versao_Software: str
   Versao_Mensageria: int