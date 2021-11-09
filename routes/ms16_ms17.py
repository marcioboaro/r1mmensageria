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
from schemas.ms07 import MS07
from cryptography.fernet import Fernet
import random
import os
import json

ms16_ms17 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

# @ms07_ms08.post("/ms16", tags=["ms16"], response_model=MS16, description="Prorrogação de reserva")
@ms16_ms17.post("/msg/v01/lockers/prolongation", tags=["ms17"], description="Prorrogação de reserva")
def ms16(ms16: MS16, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("MS16 - Prorrogação de reserva")
        logger.info(ms16)
        logger.info(public_id)

        # validando ID_do_Solicitante
        if ms16.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M017007 - ID_do_Solicitante obrigatório"}
        if len(ms16.ID_do_Solicitante) != 20: # 20 caracteres
            return {"status_code": 422, "detail": "M017011 - ID_do_Solicitante deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms16.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M017008 - ID_Rede_Lockers obrigatório"}
        if ms16.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms07.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M017008 - ID_Rede_Lockers inválido"}

        # gerando Data_Hora_Solicitacao
        if ms16.Data_Hora_Solicitacao is None:
            ms16.Data_Hora_Solicitacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # validando mensagem "Reserva não Existe"
        if ms16.ID_Transacao_Unica is None:
            return {"status_code": 422, "detail": "M017009 - ID_Transacao_Unica obrigatório"}
        if ms16.ID_Transacao_Unica is not None:
            command_sql = f"SELECT IdTransacaoUnica from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M017001 - Reserva não Existe"}

        # validando Locker
        if ms16.ID_da_Estacao_do_Locker is None:
            return {"status_code": 422, "detail": "M017008 - ID_da_Estacao_do_Locker obrigatório"}
        if ms16.ID_da_Estacao_do_Locker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{ms16.ID_da_Estacao_do_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M017021 - ID_da_Estacao_do_ Locker inválido"}

        # validando porta
        if ms16.ID_da_Porta_do_Locker is None:
            return {"status_code": 422, "detail": "M017010 - ID_da_Porta_do_Locker obrigatório"}
        if ms16.ID_da_Porta_do_Locker is not None:
            command_sql = f"SELECT idLockerPorta from locker_porta where locker_porta.idLockerPorta = '{ms16.ID_da_Porta_do_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M017023 - ID_da_Porta_do_Locker inválido"}

        # validando versao mensageria
        if ms16.Versao_Mensageria is None:
            ms16.Versao_Mensageria = "1.0.0"

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")

        ms17['Codigo_de_MSG'] = "MS17"
        ms17['ID_de_Referencia'] = ms16.ID_de_Referencia
        ms17['ID_do_Solicitante'] = ms16.ID_do_Solicitante
        ms17['ID_Rede_Lockers'] = ms16.ID_Rede_Lockers
        ms17['Codigo_Resposta_MS17'] = 'M017000 - Sucesso'
        ms17['Data_Hora_Resposta'] = dt_string
        ms17['ID_da_Estacao_do_Locker'] = ms16.ID_da_Estacao_do_Locker
        ms17['ID_da_Porta_do_Locker'] = ms16.ID_da_Porta_do_Locker
        ms17['ID_Transacao_Unica'] = ms16.ID_Transacao_Unica
        ms06['DataHora_Inicio_Reserva'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ms06['DataHora_Final_Reserva'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ms17['Versao_Mensageria'] = ms16.Versao_Mensageria
        return ms17
    except Exception as e:
        logger.error(e)
        logger.info("MS07 - Cancelamento de reserva")
        return {"status_code": 500, "detail": "MS07 - Cancelamento de reserva"}

#def send_lc01_mq(ms07, idTransacaoUnica, record_Porta, Inicio_reserva, Final_reserva):
    #try:  # Envia LC01 para fila do RabbitMQ o aplicativo do locker a pega lá


def update_reserva_encomenda(ms07, IdTransacaoUnica):
    try:
        command_sql = f"""UPDATE `reserva_encomenda`
                                            SET     `IdSolicitante` = '{ms07.ID_do_Solicitante}',
                                                    `IdReferencia` = '{ms07.ID_de_Referencia}',
                                                    `idStatusEncomenda` = '{3}',
                                                    `DateUpdate` = now()
                                            WHERE `IdTransacaoUnica` = '{ms07.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error insert_ms05'] = sys.exc_info()
        return result
