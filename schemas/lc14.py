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

class LC14(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
LC14	LC14	Resposta de Mensagem de Monitoração 					
LC14	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC14	1	Codigo_ de_ MSG	AN	4	M	LC14	Codigo da mensagem
LC14	2	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC14	3	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC14	4	Codigo_Resposta	AN	6	M		Codigo de Resposta 
LC14	5	Info_Portas					
LC14	5.1	ID_ da_ Porta_ do_ Locker	AN	42	M		ID Universal da Porta da  Estação Locker
LC14	5.2	Status_Logico_Porta					
LC14	5.3	Status_Fisico_Porta	AN				"Status Porta
01  Aberta
02  Fechada
03 Bloqueada por solicitação Central
04  OFF- Problema Fechadura
 05 OFF Vandalismo"
LC14	6	Status_Painel Tablet	N	2	M		00=OFF  01=ON
LC14	7	Status_Camera	N	2	M		00=OFF  01=ON
LC14	8	Status_Comunicação	N	2	M		00=OFF  01=ON
LC14	9	Temperatura	N	2	M		Em graus Celsius
LC14	10	Data_Hora	D	10	M		
LC14	10.1	Data	T	8	M	YYY-MM-DD	Data
LC14	10.2	Hora	AN	5	M	HH:MM:SS	Hora
LC14	10.3	Zona_ do_ Tempo	AN	12	M	(+)(-) HH:MM	Zona do Tempo
LC14	11	Versão_Software	N	4	M		Versão do software
LC14	12	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''