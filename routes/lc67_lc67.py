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
from schemas.lc67 import LC67
from cryptography.fernet import Fernet
import pika
import random
import os
import json
import requests
import logging
import random
import uuid


lc67_lc67 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

@lc67_lc67.post("/api/v01/lc67", tags=["lc67"], description="Envio dos dados da tabela Reservation")
def lc67(lc67: LC67, public_id=Depends(auth_handler.auth_wrapper)):

    try:
        logger.info("Envio dos dados da tabela Reservation")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc67.CD_MSG is None:
            lc67.CD_MSG = "LC67"

        if lc67.idRede is None:
            return {"status_code": 422, "detail": "LC6701 - idRede obrigatório"}
        if lc67.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc67.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC6702 - idRede inválido"}

        if lc67.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc67.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC6703 - IdLocker inválido"}



        now = datetime.now()
        ret_fila = send_lc67_mq(lc67)
        if ret_fila is False:
            logger.error("lc67 não inserido")

        return {"status_code": 200, "detail": "LC67000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc67'] = sys.exc_info()
        return {"status_code": 500, "detail": "lc67 - Envio dos dados da tabela Reservation"}


def send_lc67_mq(lc67):
    try: 

 
        lc067 = {}
        lc067["CD_MSG"] = "LC67"

        content = {}
        content["idRede"] = lc67.idRede
        content["idLocker"] = lc67.idLocker
        lc067["Content"] = content

        MQ_Name = 'Rede1Min_MQ'
        URL = 'amqp://rede1min:Minuto@167.71.26.87' # URL do RabbitMQ
        queue_name = lc67.idLocker + '_locker_output' # Nome da fila do RabbitMQ

        url = os.environ.get(MQ_Name, URL)
        params = pika.URLParameters(url)
        params.socket_timeout = 6

        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        message = json.dumps(lc067) # Converte o dicionario em string

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
