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
from schemas.ms11 import MS11
from cryptography.fernet import Fernet
import pika
import random
import os
import json

ms11_ms11 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

@ms11_ms11.post("/msg/v01/lockers/order/tracking", tags=["ms11"], description="Notificação de Eventos de Tracking de Reservas")
def ms11(ms11: MS11, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("Notificação de Eventos de Tracking de Reservas")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        # validando ID_do_Solicitante
        if ms11.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M012006 - ID_do_Solicitante obrigatório"}
        if len(ms11.ID_do_Solicitante) != 20:  # 20 caracteres
            return {"status_code": 422, "detail": "M012007 - ID_do_Solicitante deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms11.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M012004 - ID_Rede_Lockers obrigatório"}
        if ms11.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms11.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M012005 - ID_Rede_Lockers inválido"}

        # validando ID_Transacao_Unica
        if ms11.ID_Transacao_Unica is None:
            return {"status_code": 422, "detail": "M012002 - ID_Transacao_Unica obrigatório"}
        if ms11.ID_Transacao_Unica is not None:
            command_sql = f"SELECT IdTransacaoUnica from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M012001 - ID_Transacao_Unica não Existe"}

        # gerando Data_Hora_POD
        if ms11.Data_Hora_Notificacao_Evento_Reserva is None:
            ms11.Data_Hora_Notificacao_Evento_Reserva = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # validando versao mensageria
        if ms11.Versao_Mensageria is None:
            ms11.Versao_Mensageria = "1.0.0"

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")

        command_sql = f"""UPDATE `tracking_encomenda`
                                SET     `idStatusEncomendaAnterior` = '{ms11.Status_Reserva_Anterior}',
                                        `idStatusEncomendaAtual` = '{ms11.Status_Reserva_Atual}',
                                        `DateUpdate` = now()
                                WHERE `IdTransacaoUnica` = '{ms11.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)

        return {"status_code": 200, "detail": "M011000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms11'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS11 - Notificação de Eventos de Tracking de Reservas"}
