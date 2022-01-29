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
from schemas.lc18 import LC18
from cryptography.fernet import Fernet
import pika
import random
import os
import json
import requests
import logging


lc18_lc18 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()


@lc18_lc18.post("/api/v01/lc18", tags=["lc18"], description="Transferencia de  Carga de Nova Versão de Software")
def lc18(lc18: LC18, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("Transferencia de  Carga de Nova Versão de Software")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc18.CD_MSG is None:
            lc18.CD_MSG = "LC18"

        if lc18.idRede is None:
            return {"status_code": 422, "detail": "LC1801 - idRede obrigatório"}
        if lc18.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc18.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC1802 - idRede inválido"}

        if lc18.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc18.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC1803 - idLocker inválido"}

        if lc18.VersaoSoftware is None:
            lc18.VersaoSoftware = "0.1"


        if lc18.VersaoMensageria is None:
            lc18.VersaoMensageria = "1.0.0"

        if lc18.VersaoMensageria is not None:
            if lc18.VersaoMensageria != "1.0.0":
                return {"status_code": 422, "detail": "LC1804 - VersaoMensageria inválido"}

        if lc18.DT is None:
            lc18.DT = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if lc18.CD_NovaVersao is None:
            return {"status_code": 422, "detail": "LC1805 - CD_NovaVersao obrigatório"}

        if lc18.URL_CD_Nova_Versao is None:
            return {"status_code": 422, "detail": "LC1806 - URL_CD_Nova_Versao obrigatório"}

        if lc18.DT_TrocaVersao is None:
            lc18.DT_TrocaVersao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if lc18.URL_Script_Instalacao is None:
            return {"status_code": 422, "detail": "LC1807 - URL_Script_Instalacao obrigatório"}

        now = datetime.now()
        ret_fila = send_lc018_mq(lc18)
        if ret_fila is False:
            logger.error("lc18 não inserido")

        return {"status_code": 200, "detail": "LC18000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc18'] = sys.exc_info()
        return {"status_code": 500, "detail": "LC18 - Transferencia de Carga de Nova Versão de Software"}


def send_lc018_mq(lc18):
    try:
        lc018 = {}
        lc018["CD_MSG"] = "LC18"

        content = {}
        content["idRede"] = lc18.idRede
        content["idLocker"] = lc18.idLocker
        content["DT"] = lc18.DT
        content["CD_NovaVersao"] = lc18.CD_NovaVersao
        content["URL_CD_Nova_Versao"] = lc18.URL_CD_Nova_Versao
        content["DT_TrocaVersao"] = lc18.DT_TrocaVersao
        content["URL_Script_Instalacao"] = lc18.URL_Script_Instalacao
        content["Longitude"] = lc18.Longitude
        content["Latitude"] = lc18.Latitude
        content["Versao_Software"] = lc18.VersaoSoftware
        content["Versao_Mensageria"] = lc18.VersaoMensageria

        lc018["Content"] = content

        print(logger.warning)

        MQ_Name = 'Rede1Min_MQ'
        URL = 'amqp://rede1min:Minuto@167.71.26.87'  # URL do RabbitMQ
        queue_name = lc18.idLocker + '_locker_output'  # Nome da fila do RabbitMQ

        url = os.environ.get(MQ_Name, URL)
        params = pika.URLParameters(url)
        params.socket_timeout = 6

        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        print(logger.warning)

        channel.queue_declare(queue=queue_name, durable=True)

        print(logger.warning)

        message = json.dumps(lc018)  # Converte o dicionario em string

        channel.basic_publish(
            exchange='amq.direct',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

        connection.close()
        return True

        print(logger.warning)
    except:
        logger.error(sys.exc_info())
        return False

