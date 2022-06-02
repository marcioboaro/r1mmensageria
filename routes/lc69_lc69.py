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
from schemas.lc69 import LC69
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

lc69_lc69 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()
rabbitMq = RabbitMQ()

@lc69_lc69.post("/api/v01/lc69", tags=["lc69"], description="Envio dos dados da tabela Encomenda")
def lc69(lc69: LC69, public_id=Depends(auth_handler.auth_wrapper)):

    try:
        logger.info("Envio dos dados da tabela Reservation")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc69.CD_MSG is None:
            lc69.CD_MSG = "LC69"

        if lc69.idRede is None:
            return {"status_code": 422, "detail": "LC6901 - idRede obrigatório"}
        if lc69.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc69.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC6902 - idRede inválido"}

        if lc69.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc69.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC6903 - IdLocker inválido"}

        now = datetime.now()
        ret_fila = send_lc69_mq(lc69)
        if ret_fila is False:
            logger.error("lc69 não inserido")

        return {"status_code": 200, "detail": "LC69000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc69'] = sys.exc_info()
        return {"status_code": 500, "detail": "lc69 - Envio dos dados da tabela Reservation"}

def send_lc69_mq(lc69):
    try: 
        lc069 = {}
        lc069["CD_MSG"] = "LC69"

        content = {}
        content["idRede"] = lc69.idRede
        content["idLocker"] = lc69.idLocker
        lc069["Content"] = content

        message = json.dumps(lc069) # Converte o dicionario em string

        rabbitMq.send_locker_queue(lc69.idLocker, message)
        return True
    except:
        logger.error(sys.exc_info())
        return False
