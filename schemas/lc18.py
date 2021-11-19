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

class LC18(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
LC18	LC18	Transferencia de  Carga de Nova Versão de Software 					
LC18	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC18	1	Codigo_ de_ MSG	AN	4	M	LC18	Codigo da mensagem
LC18	2	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC18	3	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC18	4	Data_Hora	D	10	M		
LC18	4.1	Data	T	8	M	YYY-MM-DD	Data
LC18	4.2	Hora	AN	5	M	HH:MM:SS	Hora
LC18	4.3	Zona_ do_ Tempo	AN	12	M	(+)(-) HH:MM	Zona do Tempo
LC18	5	Codigo Nova Versao	N	4	M		Nova versão do software
LC18	6	URL_Codigo_Nova_Versao	AN	100	M		
LC18	7	Data_Hora_Troca_de_Versao	D	10	M		
LC18	7.1	Data	T	8	M	YYY-MM-DD	Data
LC18	7.2	Hora	AN	5	M	HH:MM:SS	Hora
LC18	7.3	Zona_ do_ Tempo	AN	12	M	(+)(-) HH:MM	Zona do Tempo
LC18	8	URL_Script_Instalação	AN	100	M		Ao receber -- Ativar
LC18	9	Longitude	AN	42	M		 ID de Posicionamento Global usando  ISO 6709
LC18	10	Latitude	AN	42	M		 ID de Posicionamento Global usando  ISO 6710
LC18	11	Versão_Software	N	4	M		Versão do software
LC18	12	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''