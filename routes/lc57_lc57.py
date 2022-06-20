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
from schemas.lc57 import LC57
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

lc57_lc57 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()
rabbitMq = RabbitMQ()

@lc57_lc57.post("/api/v01/lc57", tags=["lc57"], description="Envio log locker.engine_debug.txt")
def lc57(lc57: LC57, public_id=Depends(auth_handler.auth_wrapper)):

    try:
        logger.info("Envio log locker.engine_debug.txt")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc57.CD_MSG is None:
            lc57.CD_MSG = "LC57"

        if lc57.idRede is None:
            return {"status_code": 422, "detail": "LC5701 - idRede obrigatório"}
        if lc57.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc57.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC5702 - idRede inválido"}

        if lc57.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc57.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC5703 - IdLocker inválido"}

        now = datetime.now()
        ret_fila = send_lc57_mq(lc57)
        if ret_fila is False:
            logger.error("lc57 não inserido")

        return {"status_code": 200, "detail": "LC57000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc57'] = sys.exc_info()
        return {"status_code": 500, "detail": "lc57 - Envio log locker.engine_debug.txt"}

def send_lc57_mq(lc57):
    try: 
        lc057 = {}
        lc057["CD_MSG"] = "LC57"

        content = {}
        content["idRede"] = lc57.idRede
        content["idLocker"] = lc57.idLocker
        lc057["Content"] = content

        message = json.dumps(lc057) # Converte o dicionario em string

        rabbitMq.send_locker_queue(lc57.idLocker, message)
        return True
    except:
        logger.error(sys.exc_info())
        return False
