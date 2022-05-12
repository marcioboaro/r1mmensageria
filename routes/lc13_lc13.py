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
from schemas.lc13 import LC13
from cryptography.fernet import Fernet
import pika
import random
import os
import json
import requests
import logging
from rabbitmq import RabbitMQ

lc13_lc13 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()
rabbitMq = RabbitMQ()

@lc13_lc13.post("/api/v01/lc13", tags=["lc13"], description="Envio de Mensagem de Sonda de Monitorização da Central para Locker")
def lc13(lc13: LC13, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("Envio de Mensagem de Sonda de Monitorização da Central para Locker")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc13.CD_MSG is None:
            lc13.CD_MSG = "LC13"

        if lc13.idRede is None:
            return {"status_code": 422, "detail": "LC1301 - idRede obrigatório"}
        if lc13.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc13.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC1302 - idRede inválido"}

        if lc13.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc13.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC1303 - idLocker inválido"}

        if lc13.VersaoSoftware is None:
            lc13.VersaoSoftware = "0.1"


        if lc13.VersaoMensageria is None:
            lc13.VersaoMensageria = "1.0.0"

        if lc13.VersaoMensageria is not None:
            if lc13.VersaoMensageria != "1.0.0":
                return {"status_code": 422, "detail": "LC1304 - VersaoMensageria inválido"}

        if lc13.DT is None:
            lc13.DT = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        now = datetime.now()
        ret_fila = send_lc013_mq(lc13)
        if ret_fila is False:
            logger.error("lc13 não inserido")

        return {"status_code": 200, "detail": "LC13000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc13'] = sys.exc_info()
        return {"status_code": 500, "detail": "LC13 - Envio de Mensagem de Sonda de Monitorização da Central para Locker"}


def send_lc013_mq(lc13):
    try:
        lc013 = {}
        lc013["CD_MSG"] = "LC13"

        content = {}
        content["idRede"] = lc13.idRede
        content["idLocker"] = lc13.idLocker
        content["DT"] = lc13.DT
        content["Versao_Software"] = lc13.VersaoSoftware
        content["Versao_Mensageria"] = lc13.VersaoMensageria

        lc013["Content"] = content

        message = json.dumps(lc013)  # Converte o dicionario em string
        
        rabbitMq.send_locker_queue(lc13.idLocker, message)

        return True
    except:
        logger.error(sys.exc_info())
        return False

