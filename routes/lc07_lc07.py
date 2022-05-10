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
from schemas.lc07 import LC07
from cryptography.fernet import Fernet
import pika
import random
import os
import json
import requests
import logging
import random
import uuid
from service.rabbitmq import RabbitMQ

rabbitMq = RabbitMQ().instance()

lc07_lc07 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

@lc07_lc07.post("/api/v01/lc07", tags=["lc07"], description="Notificação da Central para Procedimentos a executar no Locker")
def lc07(lc07: LC07, public_id=Depends(auth_handler.auth_wrapper)):

    try:
        logger.info("Notificação da Central para Procedimentos a executar no Locker")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        if lc07.CD_MSG is None:
            lc07.CD_MSG = "LC07"

        if lc07.idRede is None:
            return {"status_code": 422, "detail": "LC0701 - idRede obrigatório"}
        if lc07.idRede is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{lc07.idRede}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC0702 - idRede inválido"}

        if lc07.idLocker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{lc07.idLocker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "LC0703 - IdLocker inválido"}

        if lc07.VersaoSoftware is None:
            lc07.VersaoSoftware = "0.1"

        if lc07.VersaoMensageria is None:
            lc07.VersaoMensageria = "1.0.0"

        if lc07.VersaoMensageria is not None:
            if lc07.VersaoMensageria != "1.0.0":
                return {"status_code": 422, "detail": "LC0704 - Versao_Mensageria inválido"}

        if lc07.DT_Prorrogacao is None:
            if lc07.AcaoExecutarPorta == 4:
                date_after = datetime.now() + timedelta(days=3)  # 3 é o valor Default
                Final_reserva = date_after.strftime('%Y-%m-%d %H:%M:%S')
                lc07.DT_Prorrogacao = Final_reserva
            elif lc07.AcaoExecutarPorta != 4:
                lc07.DT_Prorrogacao = None


        now = datetime.now()
        ret_fila = send_lc07_mq(lc07)
        if ret_fila is False:
            logger.error("lc07 não inserido")

        return {"status_code": 200, "detail": "LC07000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error lc07'] = sys.exc_info()
        return {"status_code": 500, "detail": "LC07 - Notificação da Central para Procedimentos a executar no Locker"}


def send_lc07_mq(lc07):
    try:  # Envia LC01 para fila do RabbitMQ o aplicativo do locker a pega lá

        command_sql = f"SELECT idLockerPortaFisica from locker_porta where locker_porta.idLockerPorta = '{lc07.idLockerPorta}';"
        record_Porta = conn.execute(command_sql).fetchone()
        idLockerPortaFisica = record_Porta[0]
        command_sql = f"""SELECT `reserva_encomenda`.`IdTransacaoUnica`,
                        `reserva_encomenda`.`idStatusReserva`
                        FROM `rede1minuto`.`reserva_encomenda`
                        where reserva_encomenda.idLockerPorta = '{lc07.idLockerPorta}'
                        order by reserva_encomenda.DataHoraInicioReserva DESC;"""
        reserva = conn.execute(command_sql).fetchone()


        lc007 = {}
        lc007["CD_MSG"] = "LC07"

        content = {}
        content["idRede"] = lc07.idRede
        content["idLocker"] = lc07.idLocker
        content["idLockerPorta"] = lc07.idLockerPorta
        content["idLockerPortaFisica"] = idLockerPortaFisica
        content["DT_Prorrogacao"] = lc07.DT_Prorrogacao
        if lc07.AcaoExecutarPorta == 1:
            content["AcaoExecutarPorta"] = 1
        if lc07.AcaoExecutarPorta == 2:
            content["AcaoExecutarPorta"] = 2
        if lc07.AcaoExecutarPorta == 5:
            NovoQRCODE = str(uuid.uuid1())
            NovoCD_PortaAbertura = str(random.randint(100000000000, 1000000000000))
            NovoQRCODE = NovoCD_PortaAbertura # Solicitação da Flash Courier
            content["AcaoExecutarPorta"] = 5
            content["NovoQRCODE"] = NovoQRCODE + "." # Por solicitação dos clientes o codigo passa a ser o mesmo da digitação
            content["NovoCD_PortaAbertura"] = NovoCD_PortaAbertura 
        if lc07.AcaoExecutarPorta == 4:
            content["AcaoExecutarPorta"] = 4
            content["ID_Transacao"] = reserva[0]
        if lc07.AcaoExecutarPorta == 3:
            print(reserva[1])
            logger.warning(reserva[1])
            # Quando tem encomenda no locker Ação = 6 (Devolução)
            if reserva[1] == 23 or reserva[1] == 24:
                content["AcaoExecutarPorta"] = 6
                content["ID_Transacao"] = reserva[0]
            # Quando não tem encomenda no locker Ação = 3 (Cancelamento de reserva)
            else:
                content["AcaoExecutarPorta"] = 3
                content["ID_Transacao"] = reserva[0]
        
        content["Versao_Software"] = lc07.VersaoSoftware
        content["Versao_Mensageria"] = lc07.VersaoMensageria

        lc007["Content"] = content

        message = json.dumps(lc007) # Converte o dicionario em string
        rabbitMq.send_locker_queue(lc07.idLocker, message)
        return True
    except:
        logger.error(sys.exc_info())
        return False
