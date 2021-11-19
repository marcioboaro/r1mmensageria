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

class LC08(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
LC08	12	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
LC08	LC-08	Resposta de Solicitação de alteração de Estado da Porta					
LC08	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC08	1	Codigo_ de_ MSG	AN	4	M	LC08	Codigo da mensagem
LC08	2	ID_ de_ Referencia	AN	42	M		ID de Referencia do Solicitante
LC08	3	ID_ do_ Solicitante 	AN	42	M		ID Universal do Solicitante
LC08	4	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC08	5	ID_Transacao_Unica	N	42	M		ID universalmente único gerado após o recebimento da reserva
LC08	6	Codigo_Resposta	AN	6	M		Codigo de Resposta 
LC08	7	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC08	8	ID_ da_ Porta_ do_ Locker	AN	42	M		ID Universal da Porta da  Estação Locker
LC08	9	Acao_Executada_na_Porta	N	2	M		"01 = Porta Bloqueada
02 = Porta Desbloqueada
03 =  Reserva da Porta Cancelada
04 = Reserva da Porta Prorrogada"
LC08	10	Data_Hora	D	10	M	YYY-MM-DD	Data
LC08	10.1	Data	T	8	M	HH:MM:SS	Hora
LC08	10.2	Hora	AN	5	M	(+)(-) HH:MM	Zona do Tempo
LC08	10.3	Zona_ do_ Tempo	AN	12	M	1.0.0	versão da mensageria
LC08	11	Versão_Software	N	4	M		Versão do software
	12	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''