# -*- coding: utf-8 -*-

from typing import Any
import sys
import uuid  # for public id
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from config.db import conn
from config.log import logger
from auth.auth import AuthHandler
from schemas.ms05 import MS05
from cryptography.fernet import Fernet
import pika
import random
import os
import json

ms05_ms06 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

# Consulta catalogo Lockers
def latlong_valid(latlong):
    try:
        ll = latlong.split(" ")
        lat = float(ll[0])
        lon = float(ll[1])
        if lat >= -90.0 and lat <= 90.0 and lon >= -180.0 and lon <= 180.0:
            return True
        else:
            return False
    except:
        return False

# @ms05_ms06.post("/ms05", tags=["ms06"], response_model=MS06, description="Consulta da disponibilidade de Portas em Locker")
@ms05_ms06.post("/msg/v01/lockers/reservation", tags=["ms06"], description="Consulta da disponibilidade de Portas em Locker")
def ms05(ms05: MS05, public_id=Depends(auth_handler.auth_wrapper)):
    try:        
        logger.info("Consulta da disponibilidade de Portas em Locker")
        logger.info(f"Usuário que fez a solicitação: {public_id}")
        if ms05.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M06006 - ID_do_Solicitante obrigatório"}
        if len(ms05.ID_do_Solicitante) != 20: # 20 caracteres
            return {"status_code": 422, "detail": "M06006 - ID_do_Solicitante deve conter 20 caracteres"}
        if ms05.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M06008 - ID_Rede_Lockers obrigatório"}
        if ms05.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms05.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M06011 - ID_Rede_Lockers inválido"}
        if ms05.Data_Hora_Solicitacao is None:
            ms05.Data_Hora_Solicitacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if ms05.ID_da_Estacao_do_Locker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{ms05.ID_da_Estacao_do_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M06023 - ID_da_Estacao_do_ Locker inválido"}

        if ms05.URL_CALL_BACK is None:
            return {"status_code": 422, "detail": "M06046 - URL para Call Back é obrigatória"}

        idTransacaoUnica = str(uuid.uuid1())
#        insert_ms05(ms05, idTransacaoUnica)
        info_encomendas = ms05.Info_Encomendas
#        for encomenda in info_encomendas:
#            insert_ms05_encomendas(idTransacaoUnica, encomenda)

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")

        ms06 = {}
        ms06['Codigo_de_MSG'] = "MS06"
        ms06['ID_de_Referencia'] = ms05.ID_de_Referencia
        ms06['ID_do_Solicitante'] = ms05.ID_do_Solicitante
        ms06['ID_Rede_Lockers'] = ms05.ID_Rede_Lockers
        ms06['ID_da_Estacao_do_Locker'] = ms05.ID_da_Estacao_do_Locker

        command_sql = f"""SELECT `locker`.`idPais`,
                                `locker`.`cep`,
                                `locker`.`LockerCidade`,
                                `locker`.`LockerBairro`,
                                `locker`.`LockerEndereco`,
                                `locker`.`LockerNumero`,
                                `locker`.`LockerComplemento`
                        FROM `rede1minuto`.`locker`
                        where locker.idLocker = '{ms05.ID_da_Estacao_do_Locker}';"""
        record = conn.execute(command_sql).fetchone()

        ms06['Codigo_Resposta_MS06'] = 'M06000 - Solicitação executada com sucesso'
        ms06['Data_Hora_Resposta'] = dt_string
        ms06['Codigo_Pais_Locker'] = record[0]
        ms06['CEP_Locker'] = record[1]
        ms06['Cidade_Locker'] = record[2]
        ms06['Bairro_Locker'] = record[3]
        ms06['Endereco_Locker'] = record[4]
        ms06['Numero_Locker'] = record[5]
        ms06['Complemento_Locker'] = record[6]

        command_sql = f"""SELECT idLockerPorta, 
                                 idLockerPortaFisica, 
                                 idOperadorLogistico
                            FROM `rede1minuto`.`locker_porta`
                            where locker_porta.idLocker = '{ms05.ID_da_Estacao_do_Locker}'
                            and idLockerPortaCategoria = '{ms05.Categoria_Porta}'
                            and idLockerPortaStatus = 1;"""
        record_Porta = conn.execute(command_sql).fetchone()   
        if record_Porta is None:
            ms06['Codigo_Resposta_MS06'] = 'M06001 - Não existe porta disponível para esta categoria'
            ms06['ID_PSL_Designado'] = None
            ms06['ID_Operador_Logistico'] = None
            ms06['ID_da_Porta_do_Locker'] = None
            ms06['ID_Transacao_Unica'] = 0
            ms06['Tipo_de_Servico_Reserva'] = 0
            ms06['DataHora_Inicio_Reserva'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ms06['DataHora_Final_Reserva'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            ms06['Codigo_Resposta_MS06'] = 'M06000 - Sucesso'
            ms06['ID_da_Porta_do_Locker'] = record_Porta[0]
            ms06['ID_do_Operador_da_Porta_Locker'] = record_Porta[2]
            command_sql = f"""UPDATE `rede1minuto`.`locker_porta`
                                SET `idLockerPortaStatus` = 2
                            where locker_porta.idLockerPorta = '{record_Porta[0]}'
                                AND idLockerPortaCategoria = '{ms05.Categoria_Porta}';"""
            conn.execute(command_sql)  

            ms06['ID_Transacao_Unica'] = idTransacaoUnica
            ms06['Tipo_de_Servico_Reserva'] = 5 # Contratação de Serviço de Reserva Com encomendas em Lockers Inteligentes

            Inicio_reserva =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            date_after = datetime.now() + timedelta(days=3) # 3 é o valor Default
            Final_reserva = date_after.strftime('%Y-%m-%d %H:%M:%S')

            ms06['DataHora_Inicio_Reserva'] = Inicio_reserva
            ms06['DataHora_Final_Reserva'] = Final_reserva

            Codigo_Abertura_Porta = random.randint(100000000000, 1000000000000)

            encomenda = {}
            encomendas = []
            info_encomendas = ms05.Info_Encomendas  
            for encomenda in info_encomendas:
                enc_temp = {}
                enc_temp['ID_Encomenda'] = encomenda.ID_Encomenda
                enc_temp['Etiqueta_Encomenda_Rede1minuto'] = "rede1minuto"
                enc_temp['Geracao_QRCODE'] = idTransacaoUnica
                enc_temp['Geracao_Codigo_Abertura_Porta'] = Codigo_Abertura_Porta
                encomendas.append(enc_temp)
            ms06['info_encomendas'] = encomendas
            ms06['Versao_Mensageria'] = ms05.Versao_Mensageria
                
            insert_reserva_simples(ms05, idTransacaoUnica, record_Porta, Inicio_reserva)  
            send_lc01_mq(ms05, idTransacaoUnica, record_Porta, Inicio_reserva, Final_reserva)

        return ms06
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms05'] = sys.exc_info()
        return result 

def send_lc01_mq(ms05, idTransacaoUnica, record_Porta, Inicio_reserva, Final_reserva):
    try:  # Envia LC01 para fila do RabbitMQ o aplicativo do locker a pega lá
        lc01 = {}
        lc01["CD_MSG"] = "LC01"

        content = {}
        content["ID_Referencia"] = ms05.ID_de_Referencia
        content["ID_Solicitante"] = ms05.ID_do_Solicitante
        content["ID_Rede"] = ms05.ID_Rede_Lockers
        content["ID_Transacao"] = idTransacaoUnica
        content["ServicoTipoAberPorta"] = None
        content["idLocker"] = ms05.ID_da_Estacao_do_Locker
        content["idLockerPorta"] = record_Porta[0]
        content["idLockerPortaFisica"] = record_Porta[1]
        content["ID_OpLog"] = record_Porta[2]
        content["OpLogAutenticacao"] = 0
        content["QRCODE"] = idTransacaoUnica
        content["CD_PortaAbertura"] = 1

        encomenda = {}
        encomendas = []
        info_encomendas = ms05.Info_Encomendas  
        for encomenda in info_encomendas:
            enc_temp = {}
            enc_temp["ID_Encomenda"] = encomenda.ID_Encomenda
            enc_temp["EncomendaRastreio"] = "Não imprementado"
            enc_temp["EncomendaBarras"] = "Não imprementado"
            encomendas.append(enc_temp)
        content["Encomendas"] = encomendas

        content["ID_LockerPortaAbertura"] = 3
        content["MascAvisoAbastecimento"] = "Frase com @ numero de Protocolo"
        content["MascAvisoRetirada"] = "Frase com @ numero de Protocolo"
        content["ExibTelaLockerprotocolo"] = 0
        content["EnvProtocoloOpCelular"] = 0
        content["DT_InicioReservaLocacao"] = Inicio_reserva
        content["DT_finalReservaLocacao"] = Final_reserva
        content["Versão_Software"] = "0.1"
        content["Versao_Mensageria"] = "1.0.0"

        lc01["Content"] = content

        MQ_Name = 'Rede1Min_MQ'
        URL = 'amqp://rede1min:Minuto@167.71.26.87' # URL do RabbitMQ
        queue_name = ms05.ID_da_Estacao_do_Locker + '_locker_output' # Nome da fila do RabbitMQ

        url = os.environ.get(MQ_Name, URL)
        params = pika.URLParameters(url)
        params.socket_timeout = 6

        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        message = json.dumps(lc01) # Converte o dicionario em string

        channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))

        connection.close()
        logger.info(sys.exc_info())

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error send_lc01_mq'] = sys.exc_info()
        return result 

def insert_ms05_encomendas(idTransacaoUnica, encomenda, ms05, record_Porta):
    try:
        command_sql = f"""INSERT INTO `reserva_encomenda`
                            (`IdTransacaoUnica`,
                            `IdEncomenda`,
                            `idShopperCPFCNPJ`,
                            `IdSolicitante`,
                            `IdReferencia`,
                            `idRede`,
                            `idLocker`,
                            `idLockerPorta`,
                            `DataHoraSolicitacao`,
                            `idStatusEncomenda`,
                            `idServicoReserva`,
                            `TipoFluxoAtual`,
                            `idLockerPortaCategoria`,
                            `GeraçãoQRCODERespostaMS06`,
                            `QRCODE`,
                            `GeraçãoCodigoAberturaPortaRespostaMS06`,
                            `CodigoAberturaPorta`,
                            `URL_CALL_BACK`,
                            `IdTicketRotaLockers`,
                            `idStatusEntregaEncomenda`,
                            `TipoAcao`,
                            `ComentarioCancelamento`)
                    VALUES
                            ('{idTransacaoUnica}'',
                            '{encomenda.ID_Encomenda}',
                            '{encomenda.CPF_CNPJ_Shopper}',
                            '{ms05.ID_do_Solicitante}',
                            '{ms05.ID_de_Referencia}',
                             {ms05.ID_Rede_Lockers},
                            '{ms05.ID_da_Estacao_do_Locker}',
                            '{record_Porta[0]}',
                            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}>,
                            {1},  
                            {5},  
                            {0},
                            {ms05.Categoria_Porta},
                            {None}>,
                            {QRCODE},
                            {None},
                            {CodigoAberturaPorta},
                            '{ms05.URL_CALL_BACK}',
                            {1},
                            {1},
                            {1},
                            {None})"""

        '''
                                    `GeraçãoQRCODERespostaMS06`,
                                    `QRCODE`,
                                    `GeraçãoCodigoAberturaPortaRespostaMS06`,
                                    `CodigoAberturaPorta`,
                                    '{ms05.URL_CALL_BACK}',
                                    `IdTicketRotaLockers`,
                                    `idStatusEntregaEncomenda`,
                                    `TipoAcao`,
                                    `ComentarioCancelamento`)
        '''


        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error insert_ms05_encomendas'] = sys.exc_info()
        return result

def insert_ms05(ms05, idTransacaoUnica):
    try:
        command_sql = f"""INSERT INTO MS05
                        ( ID_Transacao_Unica
                        ,ID_de_Referencia
                        ,ID_do_Solicitante
                        ,ID_Rede_Lockers
                        ,Data_Hora_Solicitacao
                        ,ID_da_Estacao_do_Locker
                        ,Tipo_de_Serviço_Reserva
                        ,ID_PSL_Designado
                        ,Autenticacao_Login_Operador_Logistico
                        ,Categoria_Porta
                        ,Geracao_de_QRCODE_na_Resposta_MS06
                        ,Geracao_de_Codigo_de_Abertura_de_Porta_na_Resposta_MS06
                        ,URL_CALL_BACK
                        ,Versao_Mensageria
                        )
                    VALUES
                        (
                        '{idTransacaoUnica}' 
                        , '{ms05.ID_de_Referencia}'
                        , '{ms05.ID_do_Solicitante}'
                        , {ms05.ID_Rede_Lockers}
                        , NOW() 
                        , {ms05.Tipo_de_Serviço_Reserva}
                        , '{ms05.ID_PSL_Designado}'
                        , '{ms05.Autenticacao_Login_Operador_Logistico}'
                        , '{ms05.Categoria_Porta}'
                        , '{ms05.Geracao_de_QRCODE_na_Resposta_MS06}'
                        , '{ms05.Geracao_de_Codigo_de_Abertura_de_Porta_na_Resposta_MS06}'
                        , '{ms05.URL_CALL_BACK}'
                        , '{ms05.Versao_Mensageria}'
                        );"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error insert_ms05'] = sys.exc_info()
        return result

def insert_reserva_simples(ms05, idTransacaoUnica, record_Porta, Inicio_reserva):
    try:
        command_sql = f'''INSERT INTO `rede1minuto`.`reserva_simples`
                                        (`IdTransacaoUnica`,
                                        `IdSolicitante`,
                                        `IdReferencia`,
                                        `idRede`,
                                        `idLocker`,
                                        `idLockerPorta`,
                                        `DataHoraSolicitacao`,
                                        `idStatusReserva`,
                                        `idServicoReserva`,
                                        `TipoFluxoAtual`)
                                    VALUES
                                        ('{idTransacaoUnica}',
                                        '{ms05.ID_do_Solicitante}',
                                        '{ms05.ID_de_Referencia}',
                                        {ms05.ID_Rede_Lockers},
                                        '{ms05.ID_da_Estacao_do_Locker}',
                                        '{record_Porta[0]}',
                                        '{Inicio_reserva}',
                                        {1},  
                                        {5},  
                                        {0});''' # 1 - Reserva efetivada, 2 - Reserva cancelada, 3 - Reserva em andamento, 4 - Reserva em espera
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error insert_reserva_simples'] = sys.exc_info()
        return result