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
from schemas.lc53 import LC53
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

lc53_lc53 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()
rabbitMq = RabbitMQ()

@lc53_lc53.post("/api/v01/lc53", tags=["lc53"], description="Envio busca log locker.engine_error.txt")
def lc53(lc53: LC53, public_id=Depends(auth_handler.auth_wrapper)):

    try:
        logger.info("Envio busca log locker.engine_error.txt")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc53.CD_MSG is None:
            lc53.CD_MSG = "LC53"

        if lc53.idRede is None:
            return {"status_code": 422, "detail": "LC5301 - idRede obrigatório"}
        if lc53.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc53.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC5302 - idRede inválido"}

        if lc53.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc53.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC5303 - IdLocker inválido"}

        now = datetime.now()
        ret_fila = send_lc53_mq(lc53)
        if ret_fila is False:
            logger.error("lc53 não inserido")

        return {"status_code": 200, "detail": "LC53000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc51'] = sys.exc_info()
        return {"status_code": 500, "detail": "lc53 - Envio busca log locker.engine_error.txt"}


def send_lc53_mq(lc53):
    try: 
        lc053 = {}
        lc053["CD_MSG"] = "LC53"

        content = {}
        content["idRede"] = lc53.idRede
        content["idLocker"] = lc53.idLocker
        lc053["Content"] = content

        message = json.dumps(lc053) # Converte o dicionario em string

        rabbitMq.send_locker_queue(lc53.idLocker, message)

        return True
    except:
        logger.error(sys.exc_info())
        return False
