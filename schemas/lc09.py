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

class LC09(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
LC09	LC09	SOLICITAÇÃO DE LOG IN DE OPERADOR LOGISTICO					
LC09	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC09	1	Codigo_ de_ MSG	AN	4	M	LC09	Codigo da mensagem
LC09	2	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC09	3	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC09	4	CPF	AN	16	M		CPF do Operador
LC09	5	Senha criptografada	AN	6	M		Senha cifrada
LC09	6	Data_Hora	D	10	M	YYY-MM-DD	Data
LC09	6.1	Data	T	8	M	HH:MM:SS	Hora
LC09	6.2	Hora	AN	5	M	(+)(-) HH:MM	Zona do Tempo
LC09	6.3	Zona_ do_ Tempo	AN	12	M	1.0.0	versão da mensageria
LC09	7	Versão_Software	N	4	M		Versão do software
LC09	8	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''