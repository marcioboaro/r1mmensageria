from typing import Optional
from pydantic import BaseModel
from datetime import datetime,time

class Encomendas(BaseModel):
    ID_Encomenda : str
    Numero_Mobile_Shopper : str
    Endereco_de_Email_do_Shopper : str
    CPF_CNPJ_Shopper : str
    Moeda_Shopper : str
    Valor_Encomenda_Shopper : str
    Numero_Nota_Fiscal_Encomenda_Shopper : str
    Codigo_Pais_Shopper : str
    Cidade_Shopper : str
    CEP_Shopper : str
    Bairro_Shopper : str
    Endereco_Shopper : str
    Numero_Shopper : str
    Complemento_Shopper : str
    Codigo_Rastreamento_Encomenda : str
    Codigo_Barras_Conteudo_Encomenda : str
    Descricao_Conteudo_Encomenda : str


class TransacaoUnica(BaseModel):
    ID_Transacao_Unica: str
    Status_Reserva: str
    ID_PSL_Designado: str
    Data_Hora_Designacao: datetime
    Codigo_Pais_Locker: str
    Cidade_Locker: str
    CEP_Locker: str
    Bairro_Locker: str
    Endereco_Locker: str
    Numero_Endereco_Locker: str
    Complemento_Locker: str
    ID_do_Operador_do_Locker: str
    ID_da_Estacao_do_Locker: str
    DataHora_Inicio_Reserva: datetime
    DataHora_Final_Reserva: datetime
    Tipo_de_Servico: int
    Contador_de_Encomendas_por_Designacao: int
    Info_Encomendas_por_Designacao: list[Encomendas]


class MS15(BaseModel):
    Codigo_de_MSG : str
    ID_de_Referencia: str
    ID_do_Solicitante_Designado : str
    ID_Rede_Lockers: int
    ID_do_Solicitante_Designador: str
    Codigo_Resposta_MS15: str
    Data_Hora_Resposta: Optional[datetime]
    Contador_Total_de_Encomendas_Designadas: int
    Info_Total_de_Encomendas_Designadas: list[TransacaoUnica]
    Versao_Mensageria: Optional[str]

