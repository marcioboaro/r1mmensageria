from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Portas(BaseModel):
   idLockerPorta: str

class Encomendas(BaseModel):
   idEncomenda: Optional[str]
   CodigoRastreamentoEncomenda: Optional[str]
   CodigoBarrasConteudoEncomenda: Optional[str]

class Content(BaseModel):
   idRede: int
   idLocker: str
   AcaoExecutarPorta: int
   idLockerPorta: str
   DT: datetime
   idRotaLocker: Optional[str]
   idTicketRotaLocker: Optional[str]
   TipoParada: Optional[str]
   StatusEntregaParadaLocker: Optional[str]
   Portas: list[Portas]
   encomendas: list[Encomendas]
   QRCODE: Optional[str]
   CD_PortaAbertura: Optional[str]
   TipoAcao: Optional[int]
   idTransacao: str
   Versão_Software: str
   Versao_Mensageria: str

class LC07(BaseModel):
   Codigo_de_MSG: str
   content: Optional[Content] = None


'''
LC07	LC-07	Solicitação da Central para Alteração de Estado da  Porta					
LC07	S/N	Nome do Campo	Tipo	Comprimento	M/O	Restrições	Descrição
LC07	1	Codigo_ de_ MSG	AN	4	M	LC07	Codigo da mensagem
LC07	2	ID_ de_ Referencia	AN	42	M		ID de Referencia do Solicitante
LC07	3	ID_ do_ Solicitante 	AN	42	M		ID Universal do Solicitante
LC07	4	ID_Rede	AN	4	M	0001	ID Universal da Rede   0001= Rede 1 Minuto 
LC07	5	ID_Transacao_Unica	N	42	M		ID universalmente único gerado após o recebimento da reserva
LC07	6	ID_ da_ Estacao_do_ Locker	AN	42	M		ID Universal da Estação  Locker
LC07	7	ID_ da_ Porta_ do_ Locker	AN	42	M		ID Universal da Porta da  Estação Locker
LC07	8	Acao_A_Executar_na_Porta	N	2	M		"01 = Bloquear a Porta
02 = Desbloquear a Porta
03 = Cancelar Reserva da Porta
04 = Prorrogar Reserva da Porta "
LC07	9	Periodo_ de_ Prorrogação	N	3	O		Em Unidades de horas 
LC07	10	Data_Hora	D	10	M	YYY-MM-DD	Data
LC07	10.1	Data	T	8	M	HH:MM:SS	Hora
LC07	10.2	Hora	AN	5	M	(+)(-) HH:MM	Zona do Tempo
LC07	10.3	Zona_ do_ Tempo	AN	12	M	1.0.0	versão da mensageria
LC07	11	Versão_Software	N	4	M		Versão do software
'''