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
from schemas.lc51 import LC51
from cryptography.fernet import Fernet
import pika
import random
import os
import json
import requests
import logging
import random
import uuid


lc51_lc51 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

@lc51_lc51.post("/api/v01/lc51", tags=["lc51"], description="Delete Config Device")
def lc51(lc51: LC51, public_id=Depends(auth_handler.auth_wrapper)):

    try:
        logger.info("Delete Config Device")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc51.CD_MSG is None:
            lc51.CD_MSG = "LC51"

        if lc51.idRede is None:
            return {"status_code": 422, "detail": "LC5101 - idRede obrigatório"}
        if lc51.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc51.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC5102 - idRede inválido"}

        if lc51.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc51.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC5103 - IdLocker inválido"}



        now = datetime.now()
        ret_fila = send_lc51_mq(lc51)
        if ret_fila is False:
            logger.error("lc51 não inserido")

        return {"status_code": 200, "detail": "LC51000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc51'] = sys.exc_info()
        return {"status_code": 500, "detail": "lc51 - Notificação da Central para Procedimentos a executar no Locker"}


def send_lc51_mq(lc51):
    try: 

 
        lc051 = {}
        lc051["CD_MSG"] = "LC51"

        content = {}
        content["idRede"] = lc51.idRede
        content["idLocker"] = lc51.idLocker
        lc051["Content"] = content

        MQ_Name = 'Rede1Min_MQ'
        URL = 'amqp://rede1min:Minuto@167.71.26.87' # URL do RabbitMQ
        queue_name = lc51.idLocker + '_locker_output' # Nome da fila do RabbitMQ

        url = os.environ.get(MQ_Name, URL)
        params = pika.URLParameters(url)
        params.socket_timeout = 6

        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        message = json.dumps(lc051) # Converte o dicionario em string

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
