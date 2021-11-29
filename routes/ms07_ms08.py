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
import json

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
            command_sql = f"SELECT IdTransacaoUnica from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M08001 - Reserva não Existe"}

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

        update_reserva(ms07)
        update_porta(ms07)
        update_tracking_reserva(ms07)
        update_tracking_porta(ms07)
        send_lc07_mq(ms07)

        return ms08

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms05'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS07 - Cancelamento de reserva"}


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

def update_reserva(ms07):
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
        result['Error update_ms07'] = sys.exc_info()
        return result

def update_tracking_reserva(ms07):
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
        result['Error update_tracking'] = sys.exc_info()
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

        command_sql = f"SELECT idLockerPorta, idLockerPortaFisica, idLocker from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}'";
        record_Porta = conn.execute(command_sql).fetchone()

        lc07 = {}
        lc07["CD_MSG"] = "LC07"

        content = {}
        content["ID_Referencia"] = ms07.ID_de_Referencia
        content["ID_Solicitante"] = ms07.ID_do_Solicitante
        content["ID_Rede"] = ms07.ID_Rede_Lockers
        content["ID_Transacao"] = ms07.ID_Transacao_Unica
        content["idLocker"] = record_Porta[3]
        content["AcaoExecutarPorta"] = 3
        content["idLockerPorta"] = record_Porta[0]
        content["idLockerPortaFisica"] = record_Porta[1]
        content["Versão_Software"] = "0.1"
        content["Versao_Mensageria"] = "1.0.0"

        lc07["Content"] = content

        MQ_Name = 'Rede1Min_MQ'
        URL = 'amqp://rede1min:Minuto@167.71.26.87' # URL do RabbitMQ
        queue_name = record_Porta[3] + '_locker_output' # Nome da fila do RabbitMQ

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
        result['Error send_lc07_mq'] = sys.exc_info()
        return result 
