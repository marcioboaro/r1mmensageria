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

class LC19(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
LC19	LC19	Resposta de Finalizaçao de Transferencia 					
LC19	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC19	1	Codigo_ de_ MSG	AN	4	M	LC19	Codigo da mensagem
LC19	2	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC19	3	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC19	4	Codigo_Resposta	AN	6	M		Codigo de Resposta 
LC19	5	Data_Hora					
LC19	5.1	Data	T	8	M	YYY-MM-DD	Data
LC19	5.2	Hora	AN	5	M	HH:MM:SS	Hora
LC19	5.3	Zona_ do_ Tempo	AN	12	M	(+)(-) HH:MM	Zona do Tempo
LC19	6	Versão_Software	N	4	M		Versão do software
LC19	7	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''