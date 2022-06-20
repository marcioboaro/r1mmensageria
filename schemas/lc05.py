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
   idLockerPortaOriginal: str
   idLockerPortaAbertura: str
   QRCODE: str
   CD_PortaAbertura: str
   DT: datetime
   Numero_Mobile_Operador: str
   Versão_Software: str
   Versao_Mensageria: str

class LC05(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
// LC - 05	Solicitação para Troca  de porta com problema para abastecimento
{
    "CD_MSG":"LC05",
    "Content":{
        "idShopper":"113.469.948-46",
        "idRede":"0001",
        "idTransacao":"0154af0f-2e7a-9afe-801d-5e21f3444c22",
        "idLocker":"89b6be7a-8ddf-43e1-846f-81e414c1cdea",
        "idLockerPortaOriginal":"de88c205-e08a-4b37-a306-45b7f240b79d",
        "idLockerPortaAbertura":"03",
        "QRCODE":"XXXXXXXXXXXXxx",
        "CD_PortaAbertura":"XXXXXXXXXXXXXXXXxx",
        "DT":"2021-12-10T13:45:00.000Z",
        "Numero_Mobile_Operador":"+5511954321275", 
        "Versão_Software":"0.01",
        "Versao_Mensageria":"0.01"
    }
}

LC05	LC-05	Solicitação para Troca  de porta com problema para abastecimento					
LC05	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC05	1	Codigo_ de_ MSG	AN	4	M	LC05	Codigo da mensagem
LC05	2	ID_ de_ Referencia	AN	42	M		ID de Referencia do Solicitante 
LC05	3	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC05	4	ID_Transacao_Unica	N	42	M		ID universalmente único gerado após o recebimento da reserva
LC05	5	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC05	6	ID_ da_ Porta_ do_ Locker_Original	AN	42	M		ID Universal da Porta da  Estação Locker original com problema
LC05	7	QRCODE	QR				QRCODE de abertura da Porta
LC05	8	Codigo de Abertura da Porta 	AN	12			Codigo de Abertura da Porta
LC05	9	Data_Hora			M		
LC05	9.1	Data	D	10	M	YYY-MM-DD	Data
LC05	9.2	Hora	T	8	M	HH:MM:SS	Hora
LC05	9.3	Zona_ do_ Tempo	AN	5	M	(+)(-) HH:MM	Zona do Tempo
LC05	10	Versão_Software	N	4	M		Versão do software
LC05	11	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''