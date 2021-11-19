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
   QRCODE: str

   CD_AcaoExecuta : str
   Encomendas: Optional[Encomendas]
   DT: datetime
   Versão_Software: str
   Versao_Mensageria: str

class LC03(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
// LC - 03	Notificação de Abertura de Porta e Execução de Procedimento Operacional
{
    "CD_MSG":"LC03",
    "Content":{
        "idShopper":"113.469.948-46",
        "idRede":"0001",
        "idTransacao":"0154af0f-2e7a-9afe-801d-5e21f3444c22",
        "idLocker":"89b6be7a-8ddf-43e1-846f-81e414c1cdea",
        "idLockerPorta":"de88c205-e08a-4b37-a306-45b7f240b79d",
        "idLockerPortaAbertura":"03",
        "QRCODE":"XXXXXXXXXXXXxx",
        "CD_PortaAbertura":"XXXXXXXXXXXXXXXXxx",
        "CD_AcaoExecuta":"01",
        "Encomendas":[
            {
                "idEncomenda":"e1444940-7841-4808-96b0-a290724c92f3",
                "EncomendaRastreio":"EM100027995SE",
                "EncomendaBarras":"001905009540140481606906809350314337370000000100"
            }
        ],
        "DT":"2021-12-10T13:45:00.000Z",
        "EnvioProtOpCel":"1",
        "Numero_Mobile_Operador":"+5511954321275", 
        "Versão_Software":"0.01",
        "Versao_Mensageria":"0.01"
    }
}

LC03	LC-03	Notificação de leitura QRCODE// Codigo de Abertura  e Abertura de Porta do Locker para Central					
LC03	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC03	1	Codigo_ de_ MSG	AN	4	M	LC03	Codigo da mensagem
LC03	2	ID_ de_ Referencia	AN	42	M		ID de Referencia Do Solicitante
LC03	3	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC03	4	ID_Transacao_Unica	N	42	M		ID universalmente único gerado após o recebimento da reserva
LC03	5	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC03	6	ID_ da_ Porta_ do_ Locker	AN	42	M		ID Universal da Porta da  Estação Locker
LC03	7	Dados da Abertura_Porta					
LC03	7.1	Metodo_Abertura_Porta 	AN	2			"01 = Leitura de QRCODE
02 = Digitação de Código de Abertura
03 = Misto ( Leitura de QRCODE ou Digitação de Código de Abertura ) "
LC03	7.2	QRCODE	QR				QRCODE de abertura da Porta
LC03	7.3	Codigo de Abertura da Porta 	AN	12			Codigo de Abertura da Porta
LC03	7.4	Acao_Executada	N	2	M		"01= QRCODE lido e Porta Aberta
02= QRCODE lido e não identificado porta para abertura
03= Tentativa de leitura de QRCODE com erro de leitura
04 = Código de Abertura Digitado e Porta Aberta
05 = Código de Abertura Digitado e não identificado"
LC03	8	Data_Hora			M		
LC03	8.1	Data	D	10	M	YYY-MM-DD	Data
LC03	8.2	Hora	T	8	M	HH:MM:SS	Hora
LC03	8.3	Zona_ do_ Tempo	AN	5	M	(+)(-) HH:MM	Zona do Tempo
LC03	9	Versão_Software	N	4	M		Versão do software
LC03	10	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''