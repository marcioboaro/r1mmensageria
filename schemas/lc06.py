from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Content(BaseModel):
   idShopper: str
   idRede: int
   idTransacao: str
   CD_Resposta: str
   idLocker: str
   idLockerPortaOriginal: str
   idLockerPortaNova: str
   QRCODE: str
   CD_PortaAbertura: str
   DT: datetime
   Numero_Mobile_Operador: str
   Versão_Software: str
   Versao_Mensageria: str

class LC06(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
// LC - 06	Resposta a solicitação de Troca de Porta
{
    "CD_MSG":"LC06",
    "Content":{
       "idShopper":"113.469.948-46",
       "idRede":"0001",
       "idTransacao":"0154af0f-2e7a-9afe-801d-5e21f3444c22",
       "CD_Resposta":"XXXXXX",
       "idLocker":"89b6be7a-8ddf-43e1-846f-81e414c1cdea",
       "idLockerPortaOriginal":"de88c205-e08a-4b37-a306-45b7f240b79d",
       "idLockerPortaNova":"de88c205-e08a-4b37-a306-45b7f240b79d",
       "QRCODE":"XXXXXXXXXXXXxx",
       "CD_PortaAbertura":"XXXXXXXXXXXXXXXXxx",
       "DT":"2021-12-10T13:45:00.000Z",
       "Versão_Software":"0.01",
       "Versao_Mensageria":"0.01",
    }
 }

LC06	LC-06	Resposta  para Troca  de porta com problema para abastecimento					
LC06	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC06	1	Codigo_ de_ MSG	AN	4	M	LC06	Codigo da mensagem
LC06	2	ID_ de_ Referencia	AN	42	M		ID de Referencia da Estação Locker
LC06	3	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC06	4	ID_Transacao_Unica	N	42	M		ID universalmente único gerado após o recebimento da reserva
LC06	5	Codigo_Resposta	AN	6	M		Codigo de Resposta 
LC06	6	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC06	7	ID_ da_ Porta_ do_ Locker_Original	AN	42	M		ID Universal da Porta da  Estação Locker original com problema
LC06	8	ID_ da_ Nova_Porta_ do_ Locker	AN	42	M		ID Universal da nova Porta da  Estação Locker valida
LC06	9	QRCODE	QR				QRCODE de abertura da Porta
LC06	10	Codigo de Abertura da Porta 	AN	12			Codigo de Abertura da Porta
LC06	11	Data_Hora			M		
LC06	11.1	Data	D	10	M	YYY-MM-DD	Data
LC06	11.2	Hora	T	8	M	HH:MM:SS	Hora
LC06	11.3	Zona_ do_ Tempo	AN	5	M	(+)(-) HH:MM	Zona do Tempo
LC06	12	Versão_Software	N	4	M		Versão do software
LC06	13	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''