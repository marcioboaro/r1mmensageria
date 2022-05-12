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
from schemas.lc55 import LC55
from cryptography.fernet import Fernet
import pika
import random
import os
import json
import requests
import logging
import random
import uuid
from rabbitmq import RabbitMQ

lc55_lc55 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()
rabbitMq = RabbitMQ()

@lc55_lc55.post("/api/v01/lc55", tags=["lc55"], description="Envio log locker.engine_info.txt")
def lc55(lc55: LC55, public_id=Depends(auth_handler.auth_wrapper)):

    try:
        logger.info("Envio log locker.engine_info.txt")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc55.CD_MSG is None:
            lc55.CD_MSG = "LC55"

        if lc55.idRede is None:
            return {"status_code": 422, "detail": "LC5501 - idRede obrigatório"}
        if lc55.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc55.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC5502 - idRede inválido"}

        if lc55.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc55.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC5503 - IdLocker inválido"}

        now = datetime.now()
        ret_fila = send_lc55_mq(lc55)
        if ret_fila is False:
            logger.error("lc55 não inserido")

        return {"status_code": 200, "detail": "LC55000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc55'] = sys.exc_info()
        return {"status_code": 500, "detail": "lc55 - Envio log locker.engine_info.txt"}


def send_lc55_mq(lc55):
    try: 
        lc055 = {}
        lc055["CD_MSG"] = "LC55"

        content = {}
        content["idRede"] = lc55.idRede
        content["idLocker"] = lc55.idLocker
        lc055["Content"] = content

        message = json.dumps(lc055) # Converte o dicionario em string

        rabbitMq.send_locker_queue(lc55.idLocker, message)

        return True
    except:
        logger.error(sys.exc_info())
        return False
