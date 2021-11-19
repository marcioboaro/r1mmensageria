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
   DT: datetime
   Versão_Software: str
   Versao_Mensageria: str

class LC02(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None


''' LC - 02	Resposta de Reserva  da  Porta
{
   "CD_MSG":"LC02",
   "Content":{
      "idShopper":"113.469.948-46",
      "idRede":"0001",
      "idTransacao":"0154af0f-2e7a-9afe-801d-5e21f3444c22",
      "CD_Resposta":"XXXXXX",
      "idLocker":"89b6be7a-8ddf-43e1-846f-81e414c1cdea",
      "idLockerPorta":"de88c205-e08a-4b37-a306-45b7f240b79d",
      "DT":"2021-12-10T13:45:00.000Z",
      "Versão_Software":"0.01",
      "Versao_Mensageria":"0.01"
   }
}

//Codigo_Resposta_LC02
//LC0201 Reserva Confirmada
//LC0202 Recusada - Porta em Uso
//LC0203 Recusada - Porta  Fora de Operação(Off)
//LC0204 Recusada - Travada  por solicitação
//LC0205 Versão de Software não confere
//LC0206 Erro de Formato


LC02	LC-02	Resposta de Reserva  da  Porta					
LC02	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC02	1	Codigo_ de_ MSG	AN	4	M	LC02	Codigo da mensagem
LC02	2	ID_ de_ Referencia	AN	42	M		ID de Referencia do Solicitante
LC02	3	ID_ do_ Solicitante 	AN	42	M		ID Universal do Solicitante
LC02	4	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC02	5	ID_Transacao_Unica	N	42	M		ID universalmente único gerado após o recebimento da reserva
LC02	6	Codigo_Resposta	AN	6	M		Codigo de Resposta 
LC02	7	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC02	8	ID_ da_ Porta_ do_ Locker	AN	42	M		ID Universal da Porta da  Estação Locker
LC02	9	Data_Hora	D	10	M	YYY-MM-DD	
LC02	9.1	Data	T	8	M	HH:MM:SS	Data
LC02	9.2	Hora	AN	5	M	(+)(-) HH:MM	Hora
LC02	9.3	Zona_ do_ Tempo	AN	12	M	1.0.0	Zona do Tempo
LC02	10	Versão_Software	N	4	M		Versão do software
LC02	11	Versao_Mensageria	AN	12	M	1.0.0	versão da mensageria
'''
