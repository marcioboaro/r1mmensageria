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
from schemas.ms07 import MS07
from cryptography.fernet import Fernet
import random
import os
import pika
import json
import requests


ms07_ms08 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

# @ms07_ms08.post("/ms05", tags=["ms08"], response_model=MS08, description="Cancelamento de reserva")
@ms07_ms08.post("/msg/v01/lockers/cancellation", tags=["ms08"], description="Cancelamento de reserva")
def ms07(ms07: MS07, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("MS07 - Cancelamento de reserva")
        logger.info(ms07)
        logger.info(public_id)

        # validando ID_do_Solicitante
        if ms07.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M08007 - ID_do_Solicitante obrigatório"}
        if len(ms07.ID_do_Solicitante) != 20: # 20 caracteres
            return {"status_code": 422, "detail": "M08011 - ID_do_Solicitante deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms07.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M08008 - ID_Rede_Lockers obrigatório"}
        if ms07.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms07.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M08008 - ID_Rede_Lockers inválido"}

        # gerando Data_Hora_Solicitacao
        if ms07.Data_Hora_Solicitacao is None:
            ms07.Data_Hora_Solicitacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # validando mensagem "Reserva não Existe"
        if ms07.ID_Transacao_Unica is None:
            return {"status_code": 422, "detail": "M08009 - ID_Transacao_Unica obrigatório"}
        if ms07.ID_Transacao_Unica is not None:
            command_sql = f"SELECT IdTransacaoUnica,idStatusReserva from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}';"
            record = conn.execute(command_sql).fetchone()
            if record[0] is None:
                return {"status_code": 422, "detail": "M08001 - Reserva não Existe"}
            elif record[1] == 2:
                return {"status_code": 422, "detail": "M08010 - Reserva já cancelada"}


        # validando versao mensageria
        if ms07.Versao_Mensageria is None:
            ms07.Versao_Mensageria = "1.0.0"

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")

        ms08 = {}
        ms08['Codigo_de_MSG'] = "MS08"
        ms08['ID_de_Referencia'] = ms07.ID_de_Referencia
        ms08['ID_do_Solicitante'] = ms07.ID_do_Solicitante
        ms08['ID_Rede_Lockers'] = ms07.ID_Rede_Lockers
        ms08['Codigo_Resposta_MS08'] = 'M08000 - Sucesso'
        ms08['Data_Hora_Resposta'] = dt_string
        ms08['ID_Transacao_Unica'] = ms07.ID_Transacao_Unica
        ms08['Versao_Mensageria'] = ms07.Versao_Mensageria

        command_sql = f"SELECT idStatusReserva from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}'";
        record_status = conn.execute(command_sql).fetchone()

        # Cancelamento com Encomenda no Seller
        if record_status[0] == 1 or record_status[0] == 4:
            update_reserva_encomenda_seller(ms07)
            update_tracking_reserva_seller(ms07)
            wh04_encomendaseller(ms07)
        # Cancelamento com Encomenda CD
        elif record_status[0] == 5 or record_status[0] == 15 or record_status[0] == 16 or record_status[0] == 17 or record_status[0] == 38:
            update_reserva_encomenda_cd(ms07)
            update_tracking_reserva_cd(ms07)
            wh04_encomendacd(ms07)
            #insert_ocorrencia_encomenda_cd(ms07) # Gerar requisição para Coleta de Devolução
        # Cancelamento com Encomenda Embarcada
        elif record_status[0] == 18:
            update_reserva_encomenda_embarcada(ms07)
            update_tracking_reserva_embarcada(ms07)
            wh04_encomendaembarcada(ms07)
            #insert_ocorrencia_encomenda_embarcada(ms07) # Gerar requisição para Coleta de Devolução
        # Cancelamento com Encomenda no Locker
        elif record_status[0] == 23 or record_status[0] == 24:
            update_reserva_encomenda_locker(ms07)
            update_tracking_reserva_locker(ms07)
            wh04_encomendanolocker(ms07)
            #insert_ocorrencia_encomenda_locker(ms07) # Gerar requisição para Coleta de Devolução

        update_porta(ms07)
        update_tracking_porta(ms07)
        reserva_wb03(ms07)
        ret_fila = send_lc07_mq(ms07)
        if ret_fila is False:
            logger.error("lc01 não inserido")
        return ms08

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms05'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS07 - Cancelamento de reserva"}



###################### teste no webhook a ser retirado posteriormente ###############################
def reserva_wb03(ms07):
    try:
        now = datetime.now()
        dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
        wb03 = {}
        wb03['CD_MSG'] = "WH001"
        wb03['ID_de_Referencia'] = ms07.ID_de_Referencia
        wb03['ID_Transacao_Unica'] = ms07.ID_Transacao_Unica
        wb03['Data_Hora_Resposta'] = dt_string
        wb03['CD_Resposta'] = "WH3000 - Cancelamento da reserva da porta executada"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                                        FROM `rede1minuto`.`reserva_encomenda`
                                                        where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url_wb01 = record[0]

        r = requests.post(url_wb01, data=json.dumps(wb03), headers={'Content-Type': 'application/json'})

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error reserva_wb03'] = sys.exc_info()
        return result


def wh04_encomendaseller(ms07):
    try:
        now = datetime.now()
        dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_de_Referencia'] = ms07.ID_de_Referencia
        wb04['ID_Transacao_Unica'] = ms07.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4002 - Cancelamento Reserva"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                                FROM `rede1minuto`.`reserva_encomenda`
                                                where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        r = requests.post(url, data=json.dumps(wb04), headers={'Content-Type': 'application/json'})

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error wh04_wh4002'] = sys.exc_info()
        return result


def wh04_encomendacd(ms07):
    try:
        now = datetime.now()
        dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_de_Referencia'] = ms07.ID_de_Referencia
        wb04['ID_Transacao_Unica'] = ms07.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4010 - Cancelamento com Encomenda CD"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                                FROM `rede1minuto`.`reserva_encomenda`
                                                where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        r = requests.post(url, data=json.dumps(wb04), headers={'Content-Type': 'application/json'})

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error wh04_encomendacd'] = sys.exc_info()
        return result


def wh04_encomendaembarcada(ms07):
    try:
        now = datetime.now()
        dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_de_Referencia'] = ms07.ID_de_Referencia
        wb04['ID_Transacao_Unica'] = ms07.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4019 - Cancelamento com Encomenda Embarcada"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                                FROM `rede1minuto`.`reserva_encomenda`
                                                where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        r = requests.post(url, data=json.dumps(wb04), headers={'Content-Type': 'application/json'})

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error wh04_encomendacd'] = sys.exc_info()
        return result

def wh04_encomendanolocker(ms07):
    try:
        now = datetime.now()
        dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_de_Referencia'] = ms07.ID_de_Referencia
        wb04['ID_Transacao_Unica'] = ms07.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4026 - Cancelamento com Encomenda no Locker"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                                FROM `rede1minuto`.`reserva_encomenda`
                                                where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        r = requests.post(url, data=json.dumps(wb04), headers={'Content-Type': 'application/json'})

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error wh04_encomendanolocker'] = sys.exc_info()
        return result
###################### teste no webhook a ser retirado posteriormente ###############################


def update_porta(ms07):
    try:

        command_sql = f"SELECT idLockerPorta from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}'";
        record_Porta = conn.execute(command_sql).fetchone()

        command_sql = f"""UPDATE `rede1minuto`.`locker_porta`
                                        SET `idLockerPortaStatus` = 1
                                    where locker_porta.idLockerPorta = '{record_Porta[0]}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_porta'] = sys.exc_info()
        return result


def update_reserva_encomenda_seller(ms07):
    try:

        command_sql = f"""UPDATE `reserva_encomenda`
                                            SET     `IdSolicitante` = '{ms07.ID_do_Solicitante}',
                                                    `IdReferencia` = '{ms07.ID_de_Referencia}',
                                                    `idStatusReserva` = 2,
                                                    `ComentarioCancelamento` = '{ms07.Comentario_Cancelamento_Reserva}',
                                                    `DateUpdate` = now()
                                            WHERE `IdTransacaoUnica` = '{ms07.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_reserva_encomenda_seller'] = sys.exc_info()
        return result

def update_reserva_encomenda_cd(ms07):
    try:
        command_sql = f"""UPDATE `reserva_encomenda`
                                            SET     `IdSolicitante` = '{ms07.ID_do_Solicitante}',
                                                    `IdReferencia` = '{ms07.ID_de_Referencia}',
                                                    `idStatusReserva` = 10,
                                                    `ComentarioCancelamento` = '{ms07.Comentario_Cancelamento_Reserva}',
                                                    `DateUpdate` = now()
                                            WHERE `IdTransacaoUnica` = '{ms07.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_reserva_encomenda_cd'] = sys.exc_info()
        return result

def update_reserva_encomenda_embarcada(ms07):
    try:
        command_sql = f"""UPDATE `reserva_encomenda`
                                            SET     `IdSolicitante` = '{ms07.ID_do_Solicitante}',
                                                    `IdReferencia` = '{ms07.ID_de_Referencia}',
                                                    `idStatusReserva` = 19,
                                                    `ComentarioCancelamento` = '{ms07.Comentario_Cancelamento_Reserva}',
                                                    `DateUpdate` = now()
                                            WHERE `IdTransacaoUnica` = '{ms07.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_reserva_encomenda_embarcada'] = sys.exc_info()
        return result


def update_reserva_encomenda_locker(ms07):
    try:
        command_sql = f"""UPDATE `reserva_encomenda`
                                            SET     `IdSolicitante` = '{ms07.ID_do_Solicitante}',
                                                    `IdReferencia` = '{ms07.ID_de_Referencia}',
                                                    `idStatusReserva` = 26,
                                                    `ComentarioCancelamento` = '{ms07.Comentario_Cancelamento_Reserva}',
                                                    `DateUpdate` = now()
                                            WHERE `IdTransacaoUnica` = '{ms07.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_reserva_encomenda_locker'] = sys.exc_info()
        return result

def update_tracking_reserva_seller(ms07):
    try:

        command_sql = f"SELECT idStatusReservaAtual from tracking_encomenda where tracking_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}'";
        record_status = conn.execute(command_sql).fetchone()
        command_sql = f"""UPDATE `tracking_encomenda`
                        SET     `idStatusReservaAnterior` = '{record_status[0]}',
                                `idStatusReservaAtual` = 2,
                                `DateUpdate` = now()
                        WHERE `IdTransacaoUnica` = '{ms07.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_tracking_reserva_seller'] = sys.exc_info()
        return result

def update_tracking_reserva_cd(ms07):
    try:
        command_sql = f"SELECT idStatusReservaAtual from tracking_encomenda where tracking_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}'";
        record_status = conn.execute(command_sql).fetchone()
        command_sql = f"""UPDATE `tracking_encomenda`
                        SET     `idStatusReservaAnterior` = '{record_status[0]}',
                                `idStatusReservaAtual` = 10,
                                `DateUpdate` = now()
                        WHERE `IdTransacaoUnica` = '{ms07.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_tracking_reserva_cd'] = sys.exc_info()
        return result

def update_tracking_reserva_embarcada(ms07):
    try:
        command_sql = f"SELECT idStatusReservaAtual from tracking_encomenda where tracking_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}'";
        record_status = conn.execute(command_sql).fetchone()
        command_sql = f"""UPDATE `tracking_encomenda`
                        SET     `idStatusReservaAnterior` = '{record_status[0]}',
                                `idStatusReservaAtual` = 19,
                                `DateUpdate` = now()
                        WHERE `IdTransacaoUnica` = '{ms07.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_tracking_reserva_embarcada'] = sys.exc_info()
        return result

def update_tracking_reserva_locker(ms07):
    try:
        command_sql = f"SELECT idStatusReservaAtual from tracking_encomenda where tracking_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}'";
        record_status = conn.execute(command_sql).fetchone()
        command_sql = f"""UPDATE `tracking_encomenda`
                        SET     `idStatusReservaAnterior` = '{record_status[0]}',
                                `idStatusReservaAtual` = 26,
                                `DateUpdate` = now()
                        WHERE `IdTransacaoUnica` = '{ms07.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_tracking_reserva_locker'] = sys.exc_info()
        return result

def update_tracking_porta(ms07):
    try:
        command_sql = f"SELECT idLockerPorta from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}'";
        record_Porta = conn.execute(command_sql).fetchone()
        command_sql = f"SELECT idStatusPortaAtual from tracking_portas where tracking_portas.idLockerPorta = '{record_Porta[0]}'";
        record_status = conn.execute(command_sql).fetchone()
        command_sql = f"""UPDATE `tracking_portas`
                                            SET     `idStatusPortaAnterior` = '{record_status[0]}',
                                                    `idStatusPortaAtual` = 1,
                                                    `DateUpdate` = now()
                                            WHERE `idLockerPorta` = '{record_Porta[0]}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_tracking'] = sys.exc_info()
        return result

def send_lc07_mq(ms07):
    try:  # Envia LC01 para fila do RabbitMQ o aplicativo do locker a pega lá

        command_sql = f"SELECT idLockerPorta from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}'";
        record = conn.execute(command_sql).fetchone()
        command_sql = f"SELECT idLockerPorta, idLockerPortaFisica, idLocker from locker_porta where locker_porta.idLockerPorta = '{record[0]}'";
        record_Porta = conn.execute(command_sql).fetchone()
        idLocker = record_Porta[2]
        idLockerPorta = record_Porta[0]
        idLockerPortaFisica = record_Porta[1]

        lc07 = {}
        lc07["CD_MSG"] = "LC07"

        content = {}
        content["idRede"] = ms07.ID_Rede_Lockers
        content["ID_Transacao"] = ms07.ID_Transacao_Unica
        content["idLocker"] = idLocker
        content["AcaoExecutarPorta"] = 3
        content["idLockerPorta"] = idLockerPorta
        content["idLockerPortaFisica"] = idLockerPortaFisica
        content["DT_Prorrogacao"] = None
        content["Versao_Software"] = "0.1"
        content["Versao_Mensageria"] = "1.0.0"

        lc07["Content"] = content

        MQ_Name = 'Rede1Min_MQ'
        URL = 'amqp://rede1min:Minuto@167.71.26.87' # URL do RabbitMQ
        queue_name = idLocker + '_locker_output' # Nome da fila do RabbitMQ

        url = os.environ.get(MQ_Name, URL)
        params = pika.URLParameters(url)
        params.socket_timeout = 6

        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        message = json.dumps(lc07) # Converte o dicionario em string

        channel.basic_publish(
                    exchange='amq.direct',
                    routing_key=queue_name,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))

        connection.close()
        return True
    except:
        logger.error(sys.exc_info())
        return False
