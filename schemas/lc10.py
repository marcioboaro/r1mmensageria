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

class LC10(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
LC10	LC10	RESPOSTA SOLICITAÇÃO DE LOG IN 					
LC10	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC10	1	Codigo_ de_ MSG	AN	4	M	LC10	Codigo da mensagem
LC10	4	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC10	5	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC10	6	Codigo_Resposta	AN	6	M		Codigo de Resposta 
LC10	6	CPF	AN	16	M		CPF do Operador
LC10	7	Senha criptografada	AN	6	M		Senha cifrada
LC10	8	Data_Hora	D	10	M	YYY-MM-DD	Data
LC10	8.1	Data	T	8	M	HH:MM:SS	Hora
LC10	8.2	Hora	AN	5	M	(+)(-) HH:MM	Zona do Tempo
LC10	8.3	Zona_ do_ Tempo	AN	12	M	1.0.0	versão da mensageria
LC10	9	Versão_Software	N	4	M		Versão do software
LC10	10	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''