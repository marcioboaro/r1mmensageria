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
from schemas.lc65 import LC65
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

lc65_lc65 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()
rabbitMq = RabbitMQ()

@lc65_lc65.post("/api/v01/lc65", tags=["lc65"], description="Envio dos dados da tabela Slot")
def lc65(lc65: LC65, public_id=Depends(auth_handler.auth_wrapper)):

    try:
        logger.info("Envio dos dados da tabela Slot")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc65.CD_MSG is None:
            lc65.CD_MSG = "LC65"

        if lc65.idRede is None:
            return {"status_code": 422, "detail": "LC6501 - idRede obrigatório"}
        if lc65.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc65.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC6502 - idRede inválido"}

        if lc65.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc65.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC6503 - IdLocker inválido"}

        now = datetime.now()
        ret_fila = send_lc65_mq(lc65)
        if ret_fila is False:
            logger.error("lc65 não inserido")

        return {"status_code": 200, "detail": "LC65000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc65'] = sys.exc_info()
        return {"status_code": 500, "detail": "lc65 - Envio dos dados da tabela Slot"}

def send_lc65_mq(lc65):
    try: 
        lc065 = {}
        lc065["CD_MSG"] = "LC65"

        content = {}
        content["idRede"] = lc65.idRede
        content["idLocker"] = lc65.idLocker
        lc065["Content"] = content

        message = json.dumps(lc065) # Converte o dicionario em string

        rabbitMq.send_locker_queue(lc65.idLocker, message)
        return True
    except:
        logger.error(sys.exc_info())
        return False
