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

class LC11(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
LC11	LC-11	Central Solicita Inicialização de Locker - Autoboot					
LC11	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC11	1	Codigo_ de_ MSG	AN	4	M	LC11	Codigo da mensagem
LC11	2	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC11	3	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC11	4	Data_Hora	D	10	M	YYY-MM-DD	Data
LC11	4.1	Data	T	8	M	HH:MM:SS	Hora
LC11	4.2	Hora	AN	5	M	(+)(-) HH:MM	Zona do Tempo
LC11	4.3	Zona_ do_ Tempo	AN	12	M	1.0.0	versão da mensageria
LC11	5	Versão_Software	N	4	M		Versão do software
LC11	6	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''