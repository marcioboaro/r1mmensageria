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

class LC16(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
LC16	LC16	Envio de Atualização de Mapa de Status de Portas da Central para Locker					
LC16	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC16	1	Codigo_ de_ MSG	AN	4	M	LC16	Codigo da mensagem
LC16	2	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC16	3	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC16	4	Numero-Portas	N	3	M		Numero de portas do Locker4
LC16	5	Info_Portas			M		
LC16	5.1	ID_ da_ Porta_ do_ Locker	AN	42	M		ID Universal da Porta da  Estação Locker
LC16	5.2	Status_Logico_Porta			M		
LC16	5.3	Status_Fisico_Porta	AN		M		
LC16	5.4	QRCODE associado a Porta	QRCODE		O		
LC16	5.5	Codigo_ de_ Abertura_Porta	AN	12	O		Codigo de Abertura da Porta
LC16	6	Data_Hora	D	10	M		
LC16	6.1	Data	T	8	M	YYY-MM-DD	Data
LC16	6.2	Hora	AN	5	M	HH:MM:SS	Hora
LC16	6.3	Zona_ do_ Tempo	AN	12	M	(+)(-) HH:MM	Zona do Tempo
LC16	7	Versão_Software	N	4	M		Versão do software
LC16	8	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''