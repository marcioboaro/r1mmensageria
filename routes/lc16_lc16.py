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
from schemas.lc16 import LC16
from cryptography.fernet import Fernet
import pika
import random
import os
import json
import requests
import logging
from rabbitmq import RabbitMQ

lc16_lc16 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()
rabbitMq = RabbitMQ()

@lc16_lc16.post("/api/v01/lc16", tags=["lc16"], description="Envio de Atualização de Mapa de Status de Portas da Central para Locker")
def lc16(lc16: LC16, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("Envio de Atualização de Mapa de Status de Portas da Central para Locker")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc16.CD_MSG is None:
            lc16.CD_MSG = "LC16"

        if lc16.idRede is None:
            return {"status_code": 422, "detail": "LC1601 - idRede obrigatório"}
        if lc16.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc16.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC1602 - idRede inválido"}

        if lc16.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc16.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC1603 - idLocker inválido"}

        if lc16.VersaoSoftware is None:
            lc16.VersaoSoftware = "0.1"

        if lc16.VersaoMensageria is None:
            lc16.VersaoMensageria = "1.0.0"

        if lc16.VersaoMensageria is not None:
            if lc16.VersaoMensageria != "1.0.0":
                return {"status_code": 422, "detail": "LC1604 - VersaoMensageria inválido"}

        if lc16.DT is None:
            lc16.DT = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        now = datetime.now()
        ret_fila = send_lc016_mq(lc16)
        if ret_fila is False:
            logger.error("lc16 não inserido")

        return {"status_code": 200, "detail": "LC16000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc16'] = sys.exc_info()
        return {"status_code": 500, "detail": "LC16 - Envio de Atualização de Mapa de Status de Portas da Central para Locker"}


def send_lc016_mq(lc16):
    try:
        lc016 = {}
        lc016["CD_MSG"] = "LC16"

        content = {}
        content["idRede"] = lc16.idRede
        content["idLocker"] = lc16.idLocker
        content["DT"] = lc16.DT
        content["Versao_Software"] = lc16.VersaoSoftware
        content["Versao_Mensageria"] = lc16.VersaoMensageria

        lc016["Content"] = content

        message = json.dumps(lc016)  # Converte o dicionario em string

        rabbitMq.send_locker_queue(lc16.idLocker, message)

        print("send_lc016_mq")
        return True
    except:
        logger.error(sys.exc_info())
        return False


