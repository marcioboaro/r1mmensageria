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
from schemas.ms16 import MS16
from cryptography.fernet import Fernet
import random
import os
import pika
import json
import requests


ms16_ms17 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

# @ms07_ms08.post("/ms16", tags=["ms16"], response_model=MS16, description="Prorrogação de reserva")
@ms16_ms17.post("/msg/v01/lockers/prolongation", tags=["ms17"], description="Prorrogação de reserva")
def ms16(ms16: MS16, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("MS16 - Prorrogação de reserva")
        logger.info(ms16)
        logger.info(public_id)

        # validando ID_do_Solicitante
        if ms16.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M017001 - ID_do_Solicitante obrigatório"}
        if len(ms16.ID_do_Solicitante) != 20: # 20 caracteres
            return {"status_code": 422, "detail": "M017002 - ID_do_Solicitante deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms16.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M017003 - ID_Rede_Lockers obrigatório"}
        if ms16.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms16.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M017004 - ID_Rede_Lockers inválido"}

        # gerando Data_Hora_Solicitacao
        if ms16.Data_Hora_Solicitacao is None:
            ms16.Data_Hora_Solicitacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # validando mensagem "Reserva não Existe"
        if ms16.ID_Transacao_Unica is None:
            return {"status_code": 422, "detail": "M017005 - ID_Transacao_Unica obrigatório"}
        if ms16.ID_Transacao_Unica is not None:
            command_sql = f"SELECT IdTransacaoUnica from reserva_encomenda WHERE reserva_encomenda.idStatusReserva in (1,3) and reserva_encomenda.IdTransacaoUnica = '{ms16.ID_Transacao_Unica}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M017006 - Reserva não Existe"}

        # validando Locker
        if ms16.ID_da_Estacao_do_Locker is None:
            return {"status_code": 422, "detail": "M017007 - ID_da_Estacao_do_Locker obrigatório"}
        if ms16.ID_da_Estacao_do_Locker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{ms16.ID_da_Estacao_do_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M017008 - ID_da_Estacao_do_ Locker inválido"}
            if conn.execute(command_sql).fetchone() is not None:
                command_sql = f"SELECT IdTransacaoUnica from reserva_encomenda where reserva_encomenda.idLocker = '{ms16.ID_da_Estacao_do_Locker}' and reserva_encomenda.IdTransacaoUnica = '{ms16.ID_Transacao_Unica}';"
                if conn.execute(command_sql).fetchone() is None:
                    return {"status_code": 422, "detail": "M017008 - Informe um ID_da_Estacao_do_ Locker correspondente a reserva informada "}

        # validando porta
        if ms16.ID_da_Porta_do_Locker is None:
            return {"status_code": 422, "detail": "M017009 - ID_da_Porta_do_Locker obrigatório"}
        if ms16.ID_da_Porta_do_Locker is not None:
            command_sql = f"SELECT idLockerPorta from locker_porta where locker_porta.idLockerPorta = '{ms16.ID_da_Porta_do_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M017010 - ID_da_Porta_do_Locker inválido"}
            if conn.execute(command_sql).fetchone() is not None:
                command_sql = f"SELECT IdTransacaoUnica from reserva_encomenda where reserva_encomenda.idLockerPorta = '{ms16.ID_da_Porta_do_Locker}' and reserva_encomenda.IdTransacaoUnica = '{ms16.ID_Transacao_Unica}';"
                if conn.execute(command_sql).fetchone() is None:
                    return {"status_code": 422, "detail": "M017008 - Informe um ID_da_Porta_do_Locker correspondente a reserva informada "}

        # validando versao mensageria
        if ms16.Versao_Mensageria is None:
            ms16.Versao_Mensageria = "1.0.0"

        Inicio_reserva = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_after = datetime.now() + timedelta(days=3)  # 3 é o valor Default
        Final_reserva = date_after.strftime('%Y-%m-%d %H:%M:%S')

        if ms16.DataHora_Inicio_Reserva is None:
            ms16.DataHora_Inicio_Reserva = Inicio_reserva

        if ms16.DataHora_Final_Reserva is None:
            ms16.DataHora_Final_Reserva = Final_reserva

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")

        ms17 = {}
        ms17['Codigo_de_MSG'] = "MS17"
        ms17['ID_de_Referencia'] = ms16.ID_de_Referencia
        ms17['ID_do_Solicitante'] = ms16.ID_do_Solicitante
        ms17['ID_Rede_Lockers'] = ms16.ID_Rede_Lockers
        ms17['Codigo_Resposta_MS17'] = 'M017000 - Sucesso'
        ms17['Data_Hora_Resposta'] = dt_string
        ms17['ID_da_Estacao_do_Locker'] = ms16.ID_da_Estacao_do_Locker
        ms17['ID_da_Porta_do_Locker'] = ms16.ID_da_Porta_do_Locker
        ms17['ID_Transacao_Unica'] = ms16.ID_Transacao_Unica
        ms17['DataHora_Inicio_Reserva'] = ms16.DataHora_Inicio_Reserva
        ms17['DataHora_Final_Reserva'] = ms16.DataHora_Final_Reserva
        ms17['Versao_Mensageria'] = ms16.Versao_Mensageria

        update_porta(ms16)
        update_reserva(ms16)
        update_tracking_reserva(ms16)
        update_tracking_porta(ms16)
        reserva_wb02(ms16)
        reserva_wb04(ms16)
        ret_fila = send_lc07_mq(ms16)
        if ret_fila is False:
            logger.error("lc07 não inserido")

        return ms17
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms16'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS16 - Prorrogação de reserva"}


def update_porta(ms16):
    try:

        command_sql = f"""UPDATE `rede1minuto`.`locker_porta`
                                        SET `idLockerPortaStatus` = 4
                                    where locker_porta.idLockerPorta = '{ms16.ID_da_Porta_do_Locker}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_porta'] = sys.exc_info()
        return result


def update_reserva(ms16):
    try:
        command_sql = f"""UPDATE `reserva_encomenda`
                                            SET     `idStatusReserva` = 3,
                                                    `DataHoraInicioReserva` = '{ms16.DataHora_Inicio_Reserva}',
                                                    `DataHoraFinalReserva` = '{ms16.DataHora_Final_Reserva}',
                                                    `DateUpdate` = now()
                                            WHERE `IdTransacaoUnica` = '{ms16.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_reserva'] = sys.exc_info()
        return result

def update_tracking_reserva(ms16):
    try:
        command_sql = f"SELECT idStatusReservaAtual from tracking_encomenda where tracking_encomenda.IdTransacaoUnica = '{ms16.ID_Transacao_Unica}'";
        record_status = conn.execute(command_sql).fetchone()
        command_sql = f"""UPDATE `tracking_encomenda`
                                            SET     `idStatusReservaAnterior` = '{record_status[0]}',
                                                    `idStatusReservaAtual` = 3,
                                                    `DateUpdate` = now()
                                            WHERE `IdTransacaoUnica` = '{ms16.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_tracking'] = sys.exc_info()
        return result


def update_tracking_porta(ms16):
    try:
        command_sql = f"SELECT idStatusPortaAtual from tracking_portas where tracking_portas.idLockerPorta = '{ms16.ID_da_Porta_do_Locker}'";
        record_Porta = conn.execute(command_sql).fetchone()
        command_sql = f"""UPDATE `tracking_portas`
                                            SET     `idStatusPortaAnterior` = '{record_Porta[0]}',
                                                    `idStatusPortaAtual` = 4,
                                                    `DateUpdate` = now()
                                            WHERE `idLockerPorta` = '{ms16.ID_da_Porta_do_Locker}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_tracking_porta'] = sys.exc_info()
        return result


def send_lc07_mq(ms16):
    try:  # Envia LC01 para fila do RabbitMQ o aplicativo do locker a pega lá

        command_sql = f"SELECT idLockerPorta from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms16.ID_Transacao_Unica}'";
        record = conn.execute(command_sql).fetchone()
        command_sql = f"SELECT idLockerPorta, idLockerPortaFisica, idLocker from locker_porta where locker_porta.idLockerPorta = '{record[0]}'";
        record_Porta = conn.execute(command_sql).fetchone()
        idLocker = record_Porta[2]
        idLockerPorta = record_Porta[0]
        idLockerPortaFisica = record_Porta[1]

        lc07 = {}
        lc07["CD_MSG"] = "LC07"

        content = {}
        content["idRede"] = ms16.ID_Rede_Lockers
        content["ID_Transacao"] = ms16.ID_Transacao_Unica
        content["idLocker"] = idLocker
        content["AcaoExecutarPorta"] = 4
        content["idLockerPorta"] = idLockerPorta
        content["idLockerPortaFisica"] = idLockerPortaFisica
        content["DT_Prorrogacao"] = ms16.DataHora_Final_Reserva
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



###################### teste no webhook a ser retirado posteriormente ###############################
def reserva_wb02(ms16):
    try:
        now = datetime.now()
        dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
        wb02 = {}
        wb02['CD_MSG'] = "WH002"
        wb02['ID_de_Referencia'] = ms16.ID_de_Referencia
        wb02['ID_Transacao'] = ms16.ID_Transacao_Unica
        wb02['Data_Hora_Resposta'] = dt_string
        wb02['CD_Resposta'] = "WH2000 - Prorrogação da reserva da porta executada"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                                        FROM `rede1minuto`.`reserva_encomenda`
                                                        where reserva_encomenda.IdTransacaoUnica = '{ms16.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url_wb02 = record[0]

        r = requests.post(url_wb02, data=json.dumps(wb02), headers={'Content-Type': 'application/json'})

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error reserva_wb02'] = sys.exc_info()
        return result


def reserva_wb04(ms16):
    try:
        now = datetime.now()
        dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                                                FROM `rede1minuto`.`reserva_encomenda`
                                                                where reserva_encomenda.IdTransacaoUnica = '{ms16.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)

        url = record[0]
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_de_Referencia'] = ms16.ID_de_Referencia
        wb04['ID_Transacao'] = ms16.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4001 - Prorrogação de Reserva"

        url = record[0]
        r = requests.post(url, data=json.dumps(wb04), headers={'Content-Type': 'application/json'})

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error reserva_wb04'] = sys.exc_info()
        return result

###################### teste no webhook a ser retirado posteriormente ###############################