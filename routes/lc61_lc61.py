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
from schemas.lc61 import LC61
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

lc61_lc61 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()
rabbitMq = RabbitMQ()

@lc61_lc61.post("/api/v01/lc61", tags=["lc61"], description="Limpa o arquivo de Log de Info: locker.engine_info.txt")
def lc61(lc61: LC61, public_id=Depends(auth_handler.auth_wrapper)):

    try:
        logger.info("Limpa o arquivo de Log de Info: locker.engine_info.txt")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc61.CD_MSG is None:
            lc61.CD_MSG = "LC61"

        if lc61.idRede is None:
            return {"status_code": 422, "detail": "LC6101 - idRede obrigatório"}
        if lc61.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc61.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC6102 - idRede inválido"}

        if lc61.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc61.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC6103 - IdLocker inválido"}

        now = datetime.now()
        ret_fila = send_lc61_mq(lc61)
        if ret_fila is False:
            logger.error("lc61 não inserido")

        return {"status_code": 200, "detail": "LC61000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc61'] = sys.exc_info()
        return {"status_code": 500, "detail": "lc61 - Limpa o arquivo de Log de Info: locker.engine_info.txt"}

def send_lc61_mq(lc61):
    try: 
        lc061 = {}
        lc061["CD_MSG"] = "LC61"

        content = {}
        content["idRede"] = lc61.idRede
        content["idLocker"] = lc61.idLocker
        lc061["Content"] = content

        message = json.dumps(lc061) # Converte o dicionario em string

        rabbitMq.send_locker_queue(lc61.idLocker, message)
        return True
    except:
        logger.error(sys.exc_info())
        return False
