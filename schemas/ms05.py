# -*- coding: utf-8 -*-
from typing import Optional
from pydantic import BaseModel, ValidationError, validator
from datetime import datetime,time

class Encomendas(BaseModel):
    ID_Encomenda : str
    Numero_Mobile_Shopper : str
    Endereco_de_Email_do_Shopper : str
    CPF_CNPJ_Shopper : Optional[str] = None
    Moeda_Shopper : Optional[str] = None
    Valor_Encomenda_Shopper : Optional[str] = None
    Numero_Nota_Fiscal_Encomenda_Shopper : Optional[str] = None
    Codigo_Pais_Shopper : Optional[str] = None
    Cidade_Shopper : Optional[str] = None
    CEP_Shopper : Optional[str] = None
    Bairro_Shopper : Optional[str] = None
    Endereco_Shopper : Optional[str] = None
    Numero_Shopper : Optional[str] = None
    Complemento_Shopper : Optional[str] = None
    Codigo_Rastreamento_Encomenda : Optional[str] = None
    Codigo_Barras_Conteudo_Encomenda : Optional[str] = None
    Descricao_Conteudo_Encomenda : Optional[str] = None
    Encomenda_Assegurada : Optional[int] = None
    Largura_Encomenda: Optional[int] = None
    Altura_Encomenda: Optional[int] = None
    Profundidade_Encomenda: Optional[int] = None

class MS05(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: Optional[str] = None
    ID_do_Solicitante: str
    ID_Rede_Lockers: int
    Data_Hora_Solicitacao: datetime
    ID_da_Estacao_do_Locker: str
    Tipo_de_Servico_Reserva: str
    ID_Transacao_Unica: Optional[str] = None
    ID_PSL_Designado:  Optional[int] = None
    Autenticacao_Login_Operador_Logistico: int
    Categoria_Porta: str
    Geracao_de_QRCODE_na_Resposta_MS06: int
    Geracao_de_Codigo_de_Abertura_de_Porta_na_Resposta_MS06: int
    Info_Encomendas: list[Encomendas]
    URL_CALL_BACK: str
    Versao_Mensageria: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    @validator('Data_Hora_Solicitacao', pre=True)
    def time_validate(cls, v):
        return datetime.fromisoformat(v)

'''
{
  "Codigo_de_MSG": "MS5",
  "ID_de_Referencia": "1455444",
  "ID_do_Solicitante": "12023895000169",
  "ID_Rede_Lockers": "1",
  "Data_Hora_Solicitacao": null,
  "ID_da_Estacao_do_Locker": "05087d0d-0433-11ec-ba8c-0022484cea46",
  "Tipo_de_Serviço_Reserva": null,
  "ID_Transacao_Unica": "2525",
  "ID_PSL_Designado": null,
  "Autenticacao_Login_Operador_Logistico": null,
  "Categoria_Porta": null,
  "Geracao_de_QRCODE_na_Resposta_MS06": null,
  "Geracao_de_Codigo_de_Abertura_de_Porta_na_Resposta_MS06": null,
  "Info_Encomendas": [{
    "ID_Encomenda": 33,
    "Numero_Mobile_Shopper": null, # validar nulo e limite
    "Endereço_de_Email_do_Shopper": # null, validar nulo e mascara
    "CPF_CNPJ_Shopper": null, # validar apenas numero
    "Moeda_Shopper": null, # validar na tabela
    "Valor_Encomenda_Shopper": null,
    "Numero_Nota_Fiscal_Encomenda_Shopper": null, 
    "Codigo_País_Shopper": null, # validar na tabela
    "Cidade_Shopper": null,
    "CEP_Shopper": null, # validar numero
    "Bairro_Shopper": null,
    "Endereco_Shopper": null,
    "Numero_Shopper": null,
    "Complemento_Shopper": null,
    "Codigo_Rastreamento_Encomenda": null,
    "Codigo_barras_conteudo_Encomenda": null,
    "Descricao_conteudo_Encomenda": null,
    "Encomenda_Assegurada": null,
    "Largura_Encomenda": 2,
    "Altura_Encomenda": null,
    "Profundidade_Encomenda": null
  },{
    "ID_Encomenda": 32,
    "Numero_Mobile_Shopper": null,
    "Endereço_de_Email_do_Shopper": null,
    "CPF_CNPJ_Shopper": null,
    "Moeda_Shopper": null,
    "Valor_Encomenda_Shopper": null,
    "Numero_Nota_Fiscal_Encomenda_Shopper": null,
    "Codigo_País_Shopper": null,
    "Cidade_Shopper": null,
    "CEP_Shopper": null,
    "Bairro_Shopper": null,
    "Endereco_Shopper": null,
    "Numero_Shopper": null,
    "Complemento_Shopper": null,
    "Codigo_Rastreamento_Encomenda": "2555611333",
    "Codigo_barras_conteudo_Encomenda": "15465444566",
    "Descricao_conteudo_Encomenda": null,
    "Encomenda_Assegurada": null,
    "Largura_Encomenda": 2,
    "Altura_Encomenda": null,
    "Profundidade_Encomenda": null
  }],
  "URL_CALL_BACK": null,
  "Versao_Mensageria": null
}

'''