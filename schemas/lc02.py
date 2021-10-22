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

clas LC02(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

'''
LC - 02	Resposta de Reserva  da  Porta
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

Codigo_Resposta_LC02
LC0201 Reserva Confirmada
LC0202 Recusada - Porta em Uso
LC0203 Recusada - Porta  Fora de Operação(Off)
LC0204 Recusada - Travada  por solicitação
LC0205 Versão de Software não confere
LC0206 Erro de Formato
'''