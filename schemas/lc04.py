from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Content(BaseModel):
   idShopper: str
   idRede: int
   idTransacao: str
   CD_Resposta: str
   idLocker: str
   idLockerPorta: str
   QRCODE: str
   CD_PortaAbertura: str
   DT: datetime
   Versão_Software: str
   Versao_Mensageria: str

class LC04(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
// LC - 04	Resposta de Notificação de Abertura de Porta e Execução de Procedimento Operacional
{
    "CD_MSG":"LC04",
    "Content":{
       "idShopper":"113.469.948-46",
       "idRede":"0001",
       "idTransacao":"0154af0f-2e7a-9afe-801d-5e21f3444c22",
       "CD_Resposta":"XXXXXX",
       "idLocker":"89b6be7a-8ddf-43e1-846f-81e414c1cdea",
       "idLockerPorta":"de88c205-e08a-4b37-a306-45b7f240b79d",
       "QRCODE":"XXXXXXXXXXXXxx",
       "CD_PortaAbertura":"XXXXXXXXXXXXXXXXxx",
       "DT":"2021-12-10T13:45:00.000Z",
       "Versão_Software":"0.01",
       "Versao_Mensageria":"0.01",
 
    }
 }
 
LC04	LC-04	Resposta de Notificação Recebida					
LC04	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC04	1	Codigo_ de_ MSG	AN	4	M	LC04	Codigo da mensagem
LC04	2	ID_ de_ Referencia	AN	42	M		ID de Referencia do Solicitante 
LC04	3	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC04	4	ID_Transacao_Unica	N	42	M		ID universalmente único gerado após o recebimento da reserva
LC04	5	Codigo_Resposta	AN	6	M		Codigo de Resposta 
LC04	6	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC04	7	ID_ da_ Porta_ do_ Locker	AN	42	M		ID Universal da Porta da  Estação Locker
LC04	8	QRCODE	QR				QRCODE de abertura da Porta
LC04	9	Codigo de Abertura da Porta 	AN	12			Codigo de Abertura da Porta
LC04	10	Data_Hora			M		
LC04	10.1	Data	D	10	M	YYY-MM-DD	Data
LC04	10.2	Hora	T	8	M	HH:MM:SS	Hora
LC04	10.3	Zona_ do_ Tempo	AN	5	M	(+)(-) HH:MM	Zona do Tempo
LC04	11	Versão_Software	N	4	M		Versão do software
LC04	12	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''