from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Encomendas(BaseModel):
   idEncomenda: str
   EncomendaRastreio: str
   EncomendaBarras: str

class Content(BaseModel):
   idShopper: str
   idRede: int
   idTransacao: str
   CD_Resposta: str
   idLocker: str
   idLockerPorta: str
   DT: datetime
   Versão_Software: str
   Versao_Mensageria: str

class LC13(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
LC13	LC13	Envio de Mensagem de Sonda de Monitoração  da Central para Locker					
LC13	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC13	1	Codigo_ de_ MSG	AN	4	M	LC13	Codigo da mensagem
LC13	2	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC13	3	ID_ da_ Estacao_do_ Locker	AN	42	M		
LC13	4	Data_Hora			M		
LC13	4.1	Data	D	10	M	YYY-MM-DD	Data
LC13	4.2	Hora	T	8	M	HH:MM:SS	Hora
LC13	4.3	Zona_ do_ Tempo	AN	5	M	(+)(-) HH:MM	Zona do Tempo
LC13	5	Versão_Software	N	4	M		Versão do software
LC13	6	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''