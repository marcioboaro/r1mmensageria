from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Portas(BaseModel):
   idLockerPorta: Optional[str]

class Encomendas(BaseModel):
   idEncomenda: Optional[str]
   CodigoRastreamentoEncomenda: Optional[str]
   CodigoBarrasConteudoEncomenda: Optional[str]
   QRCODE: Optional[str]
   CD_PortaAbertura: Optional[str]
   TipoAcao: Optional[int]
   idTransacao: Optional[str]

class LC07(BaseModel):
   CD_MSG: str
   idRede: int
   idLocker: str
   AcaoExecutarPorta: int
   idLockerPorta: str
   DT_Prorrogacao: Optional[datetime]
   idRotaLocker: Optional[str]
   idTicketRotaLocker: Optional[str]
   TipoParada: Optional[int]
   StatusEntregaParadaLocker: Optional[str]
   Portas: list[Portas]
   Info_Encomendas: list[Encomendas]
   VersaoSoftware: Optional[str]
   VersaoMensageria: Optional[str]




'''


Procedimento de  Rota 
ID_ da_ Rota_Locker 
ID_TICKET_ROTA_LOCKERS
Tipo_de_Parada
Status_de_Entrega_Parada_Locker
Numero_Portas_Parada
ID_ da_ Porta_do_ Locker
Numero_Encomendas_Parada
Info_Encomendas
ID_Encomenda
Codigo_Rastreamento_Encomenda 
Codigo_barras_conteudo_Encomenda
 QRCODE 
 Código de Abertura de Porta  
Tipo de Açao 
ID_Transacao_Unica
Versão_Software
Versao_Mensageria
'''