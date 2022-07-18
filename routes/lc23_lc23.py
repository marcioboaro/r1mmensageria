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
from schemas.lc23 import LC23
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

lc23_lc23 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()
rabbitMq = RabbitMQ()

@lc23_lc23.post("/api/v01/lc23", tags=["lc23"], description="Abertura de porta de Manutenção do Locker")
def lc23(lc23: LC23, public_id=Depends(auth_handler.auth_wrapper)):

    try:
        logger.info(f"Abertura de porta de Manutenção do Locker")
        logger.info(f"Usuário que fez a solicitação: {public_id}")
        logger.info(f"LC23: {lc23}")

        if lc23.CD_MSG is None:
            lc23.CD_MSG = "LC23"

        if lc23.idRede is None:
            return {"status_code": 422, "detail": "lc2301 - idRede obrigatório"}

        if lc23.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc23.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC2302 - idRede inválido"}

        if lc23.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc23.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC2303 - IdLocker inválido"}

        return {"status_code": 204, "detail": "LC23 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc23'] = sys.exc_info()
        return {"status_code": 500, "detail": "LC23 - Notificação da Central para Procedimentos a executar no Locker"}

def send_lc23_mq(lc23):
    try:  # Envia lc23 para fila do RabbitMQ o aplicativo do locker a pega lá

        lc230 = {}
        lc230["CD_MSG"] = "lc03"

        content = {}
        content["idRede"] = lc23.idRede
        content["idLocker"] = lc23.idLocker

        lc230["Content"] = content

        message = json.dumps(lc23) # Converte o dicionario em string

        rabbitMq.send_locker_queue(lc23.idLocker, message)
        return True

    except:
        logger.error(sys.exc_info())
        return False
