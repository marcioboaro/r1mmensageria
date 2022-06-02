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
from schemas.lc11 import LC11
from cryptography.fernet import Fernet
import pika
import random
import os
import json
import requests
import logging
from rabbitmq import RabbitMQ

lc11_lc11 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()
rabbitMq = RabbitMQ()

@lc11_lc11.post("/api/v01/lc11", tags=["lc11"], description="Central Solicita Inicialização de Locker - Autoboot")
def lc11(lc11: LC11, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("Central Solicita Inicialização de Locker - Autoboot")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc11.CD_MSG is None:
            lc11.CD_MSG = "LC11"

        if lc11.idRede is None:
            return {"status_code": 422, "detail": "LC1101 - idRede obrigatório"}
        if lc11.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc11.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC1102 - idRede inválido"}

        if lc11.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc11.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC1603 - IdLocker inválido"}

        if lc11.VersaoSoftware is None:
            lc11.VersaoSoftware = "0.1"

        if lc11.VersaoMensageria is None:
            lc11.VersaoMensageria = "1.0.0"

        if lc11.VersaoMensageria is not None:
            if lc11.VersaoMensageria != "1.0.0":
                return {"status_code": 422, "detail": "LC1104 - VersaoMensageria inválido"}

        if lc11.DT is None:
            lc11.DT = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        now = datetime.now()
        ret_fila = send_lc011_mq(lc11)
        if ret_fila is False:
            logger.error("lc11 não inserido")

        return {"status_code": 200, "detail": "LC11000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc11'] = sys.exc_info()
        return {"status_code": 500, "detail": "LC11 - Central Solicita Inicialização de Locker - Autoboot"}

def send_lc011_mq(lc11):
    try:
        lc011 = {}
        lc011["CD_MSG"] = "LC11"

        content = {}
        content["idRede"] = lc11.idRede
        content["idLocker"] = lc11.idLocker
        content["DT"] = lc11.DT
        content["Versao_Software"] = lc11.VersaoSoftware
        content["Versao_Mensageria"] = lc11.VersaoMensageria

        lc011["Content"] = content

        message = json.dumps(lc011)  # Converte o dicionario em string

        rabbitMq.send_locker_queue(lc11.idLocker, message)

        return True
    except:
        logger.error(sys.exc_info())
        return False