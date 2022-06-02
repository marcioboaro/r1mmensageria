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
   Tipo_de_Servico_Reserva: int
   idLocker: str
   idLockerPorta: str
   idOpLog: str
   OpLogAutenticacao: bool
   QRCODE: str
   CD_PortaAbertura: str
   encomendas: Optional[Encomendas] = None
   idLockerPortaAbertura: int
   MascAvisoAbastecimento: str
   MascAvisoRetirada: str
   ExibTelaLockerprotocolo: bool
   EnvProtocoloOpCelular: bool
   DT_InicioReservaLocacao: datetime
   DT_finalReservaLocacao: datetime
   Versao_Software: str
   Versao_Mensageria: int

class LC01(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None

''' LC - 01	Solicitação deReserva de Porta
{
   "CD_MSG":"LC01",
   "Content":{
      "idShopper":"113.469.948-46",
      "idRede":"0001",
      "idTransacao":"0154af0f-2e7a-9afe-801d-5e21f3444c22",
      "ServicoTipoAberPorta":"01", // 01 à 11
      "idLocker":"89b6be7a-8ddf-43e1-846f-81e414c1cdea",
      "idLockerPorta":"de88c205-e08a-4b37-a306-45b7f240b79d",
      "idOpLog":"9dd547bd-e706-4a74-8db5-20fd77a44278",
      "OpLogAutenticacao":"1",       //	0 = NÃO  1 = SIM
      "QRCODE":"XXXXXXXXXXXXxx",
      "CD_PortaAbertura":"XXXXXXXXXXXXXXXXxx",
      "Encomendas":[
         {
            "idEncomenda":"e1444940-7841-4808-96b0-a290724c92f3",
            "EncomendaRastreio":"EM100027995SE",
            "EncomendaBarras":"001905009540140481606906809350314337370000000100"
         }
      ],
      "idLockerPortaAbertura":"03",
      "MascAvisoAbastecimento":"Por favor tome cuidado é quebravel",
      "MascAvisoRetirada":"Por favor tome cuidado é quebravel",
      "ExibTelaLockerprotocolo":"1",    //	0 = NÃO  1 = SIM
      "EnvProtocoloOpCelular":"1",      //	0 = NÃO  1 = SIM
      "DT_InicioReservaLocacao":"2021-12-10T13:45:00.000Z",
      "DT_finalReservaLocacao":"2021-12-12T13:45:00.000Z",
      "Versão_Software":"0.01",
      "Versao_Mensageria":"0.01"
   }
}
'''
