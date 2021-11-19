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

class LC17(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
LC17	LC17	Resposta de Atualização de Mapas de Status					
LC17	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC17	1	Codigo_ de_ MSG	AN	4	M	LC16	Codigo da mensagem
LC17	2	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC17	3	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC17	4	Codigo_Resposta	AN	6	M		Codigo de Resposta 
LC17	5	Data_Hora	D	10	M		
LC17	5.1	Data	T	8	M	YYY-MM-DD	Data
LC17	5.2	Hora	AN	5	M	HH:MM:SS	Hora
LC17	5.3	Zona_ do_ Tempo	AN	12	M	(+)(-) HH:MM	Zona do Tempo
LC17	6	Versão_Software	N	4	M		Versão do software
LC17	7	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''