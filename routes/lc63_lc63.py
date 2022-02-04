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
from schemas.lc63 import LC63
from cryptography.fernet import Fernet
import pika
import random
import os
import json
import requests
import logging
import random
import uuid


lc63_lc63 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

@lc63_lc63.post("/api/v01/lc63", tags=["lc63"], description="Envio dos dados da tabela Device")
def lc63(lc63: LC63, public_id=Depends(auth_handler.auth_wrapper)):

    try:
        logger.info("Envio dos dados da tabela Device")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc63.CD_MSG is None:
            lc63.CD_MSG = "LC63"

        if lc63.idRede is None:
            return {"status_code": 422, "detail": "LC6301 - idRede obrigatório"}
        if lc63.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc63.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC6302 - idRede inválido"}

        if lc63.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc63.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC6303 - IdLocker inválido"}



        now = datetime.now()
        ret_fila = send_lc63_mq(lc63)
        if ret_fila is False:
            logger.error("lc63 não inserido")

        return {"status_code": 200, "detail": "LC63000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc63'] = sys.exc_info()
        return {"status_code": 500, "detail": "lc63 - Envio dos dados da tabela Device"}


def send_lc63_mq(lc63):
    try: 

 
        lc063 = {}
        lc063["CD_MSG"] = "LC63"

        content = {}
        content["idRede"] = lc63.idRede
        content["idLocker"] = lc63.idLocker
        lc063["Content"] = content

        MQ_Name = 'Rede1Min_MQ'
        URL = 'amqp://rede1min:Minuto@167.71.26.87' # URL do RabbitMQ
        queue_name = lc63.idLocker + '_locker_output' # Nome da fila do RabbitMQ

        url = os.environ.get(MQ_Name, URL)
        params = pika.URLParameters(url)
        params.socket_timeout = 6

        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        message = json.dumps(lc063) # Converte o dicionario em string

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
