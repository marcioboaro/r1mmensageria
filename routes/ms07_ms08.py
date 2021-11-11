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

ms07_ms08 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

# @ms07_ms08.post("/ms05", tags=["ms08"], response_model=MS08, description="Cancelamento de reserva")
@ms07_ms08.post("/msg/v01/lockers/cancellation", tags=["ms08"], description="Cancelamento de reserva")
def ms07(ms07: MS07, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("MS07 - Cancelamento de reserva")
        logger.info(ms07)
        logger.info(public_id)

        # validando ID_do_Solicitante
        if ms07.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M08007 - ID_do_Solicitante obrigatório"}
        if len(ms07.ID_do_Solicitante) != 20: # 20 caracteres
            return {"status_code": 422, "detail": "M08011 - ID_do_Solicitante deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms07.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M08008 - ID_Rede_Lockers obrigatório"}
        if ms07.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms07.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M08008 - ID_Rede_Lockers inválido"}

        # gerando Data_Hora_Solicitacao
        if ms07.Data_Hora_Solicitacao is None:
            ms07.Data_Hora_Solicitacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # validando mensagem "Reserva não Existe"
        if ms07.ID_Transacao_Unica is None:
            return {"status_code": 422, "detail": "M08009 - ID_Transacao_Unica obrigatório"}
        if ms07.ID_Transacao_Unica is not None:
            command_sql = f"SELECT IdTransacaoUnica from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms07.ID_Transacao_Unica}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M08001 - Reserva não Existe"}

        # validando versao mensageria
        if ms07.Versao_Mensageria is None:
            ms07.Versao_Mensageria = "1.0.0"

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")

        ms08 = {}
        ms08['Codigo_de_MSG'] = "MS08"
        ms08['ID_de_Referencia'] = ms07.ID_de_Referencia
        ms08['ID_do_Solicitante'] = ms07.ID_do_Solicitante
        ms08['ID_Rede_Lockers'] = ms07.ID_Rede_Lockers
        ms08['Codigo_Resposta_MS08'] = 'M08000 - Sucesso'
        ms08['Data_Hora_Resposta'] = dt_string
        ms08['ID_Transacao_Unica'] = ms07.ID_Transacao_Unica
        idTransacaoUnica = ms07.ID_Transacao_Unica
        update_ms07(ms07, idTransacaoUnica)
        ms08['Versao_Mensageria'] = ms07.Versao_Mensageria
        return ms08

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms05'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS07 - Cancelamento de reserva"}

#def send_lc01_mq(ms07, idTransacaoUnica, record_Porta, Inicio_reserva, Final_reserva):
    #try:  # Envia LC01 para fila do RabbitMQ o aplicativo do locker a pega lá


def update_ms07(ms07, idTransacaoUnica):
    try:
        command_sql = f"""UPDATE `reserva_encomenda`
                                            SET     `IdSolicitante` = '{ms07.ID_do_Solicitante}',
                                                    `IdReferencia` = '{ms07.ID_de_Referencia}',
                                                    `idStatusEncomenda` = 2,
                                                    `ComentarioCancelamento` = '{ms07.Comentario_Cancelamento_Reserva}',
                                                    `DateUpdate` = now()
                                            WHERE `IdTransacaoUnica` = '{ms07.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error insert_ms06'] = sys.exc_info()
        return result
