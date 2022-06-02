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

class LC15(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
LC15	LC15	Notificação  do  Locker para Central					
LC15	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC15	1	Codigo_ de_ MSG	AN	4	M	LC15	Codigo da mensagem
LC15	2	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC15	3	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC15	4	Info_Portas			M		
LC15	4.1	ID_ da_ Porta_ do_ Locker	AN	42	M		ID Universal da Porta da  Estação Locker Se evento de falha na porta campo obrigatorio , nas demais ignorar 
LC15	4.2	Status_Porta	AN	2	M		"Status Porta
01  Aberta
02  Fechada
03 Bloqueada por solicitação Central
04  OFF- Problema Fechadura
 05 OFF Vandalismo"
LC15	5	Status_Painel Tablet	N	2	M		00=OFF  01=ON
LC15	6	Status_Camera	N	2	M		00=OFF  01=ON
LC15	7	Status_Comunicação	N	2	M		00=OFF  01=ON
LC15	8	Temperatura	N	2	M		Em graus Celsius
LC15	9	Queda de Energia	N	2	M		Informar na data e hora da ocorrencia da queda e enviar Notificação imediatamente após Reinicialização automatica do aplicativo do Locker
LC15	10	Acao-Requerida	N	2	O		01 = Enviar Mapa de Atualização
LC15	11	Data__Hora_Ocorrencia	D	10	M		
LC15	11.1	Data	T	8	M	YYY-MM-DD	Data
LC15	11.2	Hora	AN	5	M	HH:MM:SS	Hora
LC15	11.3	Zona_ do_ Tempo	AN	12	M	(+)(-) HH:MM	Zona do Tempo
LC15	12	Data_Hora_Atual	D	10	M		
LC15	12.1	Data	T	8	M	YYY-MM-DD	Data
LC15	12.2	Hora	AN	5	M	HH:MM:SS	Hora
LC15	12.3	Zona_ do_ Tempo	AN	12	M	(+)(-) HH:MM	Zona do Tempo
LC15	13	Versão_Software	N	4	M		Versão do software
LC15	14	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''