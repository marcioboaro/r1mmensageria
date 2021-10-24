from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class Encomendas(BaseModel):
    ID_Encomenda: str
    Etiqueta_Encomenda_Rede1minuto: str
    Geracao_QRCODE: str
    Geracao_Codigo_Abertura_Porta: str

class MS06(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    ID_da_Estacao_do_Locker: str
    Codigo_Resposta_MS06: str
    Data_Hora_Resposta: datetime
    Codigo_Pais_Locker: str
    Cidade_Locker: str
    CEP_Locker: str
    Bairro_Locker: str
    Endereco_Locker: str
    Numero_Locker: str
    Complemento_Locker: str
    ID_do_Operador_da_Porta_Locker: str
    ID_da_Porta_do_Locker: str
    ID_Transacao_Unica: str
    Tipo_de_Servico_Reserva: str
    DataHora_Inicio_Reserva: datetime
    DataHora_Final_Reserva: datetime
    Info_Encomendas: list[Encomendas]
    Versao_Mensageria: str

''' {
  "Codigo_de_MSG": "MS06",
  "ID_de_Referencia": "a2e8505f-8f38-4826-8849-103217fb568b",
  "ID_do_Solicitante": "12023895000169",
  "ID_Rede_Lockers": 1,
  "ID_da_Estacao_do_Locker": "05087d0d-0433-11ec-ba8c-0022484cea46",
  "Codigo_Resposta_MS06": "string",
  "Data_Hora_Resposta": "2021-09-21T16:07:21",
  "Codigo_Pais_Locker": "BR",
  "Cidade_Locker": "São Paulo",
  "CEP_Locker": "01417020",
  "Bairro_Locker": "Centro",
  "Endereco_Locker": "Rua A",
  "Numero_Locker": "320",
  "Complemento_Locker": null,
  "ID_do_Operador_da_Porta_Locker": "77310f64-6695-4e2e-ab2b-be76e549708d",
  "ID_da_Porta_do_Locker": "1c79c3ba-f71e-11eb-aca9-0022484cea46",
  "ID_Transacao_Unica": 456645521123,
  "Tipo_de_Servico_Reserva": "Nova Reserva com Encomenda para Retirada",
  "DataHora_Inicio_Reserva": "2021-09-21T16:07:40",
  "DataHora_Final_Reserva": "2021-09-23T16:07:40",
  "Info_Encomendas": [{
    "ID_Encomenda": "16555a8a-d8ce-46b0-997d-4f0f448623f0",
    "Etiqueta_Encomenda_Rede1minuto": "string",
    "Geracao_QRCODE": "string",
    "Geracao_Codigo_Abertura_Porta": "string"
  },{
    "ID_Encomenda": "16555a8a-d8ce-46b0-997d-4f0f448623f0",
    "Etiqueta_Encomenda_Rede1minuto": "string",
    "Geracao_QRCODE": "string",
    "Geracao_Codigo_Abertura_Porta": "string"
  }],
  "Versao_Mensageria": "1.0.0"
}
'''