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
from schemas.lc59 import LC59
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

lc59_lc59 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()
rabbitMq = RabbitMQ()

@lc59_lc59.post("/api/v01/lc59", tags=["lc59"], description="Limpa o arquivo de Log de Erro: locker.engine_error.txt")
def lc59(lc59: LC59, public_id=Depends(auth_handler.auth_wrapper)):

    try:
        logger.info("Limpa o arquivo de Log de Erro: locker.engine_error.txt")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc59.CD_MSG is None:
            lc59.CD_MSG = "LC59"

        if lc59.idRede is None:
            return {"status_code": 422, "detail": "LC5901 - idRede obrigatório"}
        if lc59.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc59.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC5902 - idRede inválido"}

        if lc59.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc59.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC5903 - IdLocker inválido"}

        now = datetime.now()
        ret_fila = send_lc59_mq(lc59)
        if ret_fila is False:
            logger.error("lc59 não inserido")

        return {"status_code": 200, "detail": "LC59000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc59'] = sys.exc_info()
        return {"status_code": 500, "detail": "lc59 - Limpa o arquivo de Log de Erro: locker.engine_error.txt"}


def send_lc59_mq(lc59):
    try: # Insere no RabbitMQ
        lc059 = {}
        lc059["CD_MSG"] = "LC59"

        content = {}
        content["idRede"] = lc59.idRede
        content["idLocker"] = lc59.idLocker
        lc059["Content"] = content

        message = json.dumps(lc059) # Converte o dicionario em string

        rabbitMq.send_locker_queue(lc59.idLocker, message)
        return True
    except:
        logger.error(sys.exc_info())
        return False
