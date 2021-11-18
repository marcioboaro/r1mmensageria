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
from schemas.ms12 import MS12, pod
from cryptography.fernet import Fernet
import random
import os
import json

ms12_ms12 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

@ms12_ms12.post("/msg/v01/lockers/pod", tags=["ms12"], description="Notificação de Prova de Entrega (POD)")
def ms12(ms12: MS12, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("Notificação de Prova de Entrega (POD)")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        # validando ID_do_Solicitante
        if ms12.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M012006 - ID_do_Solicitante obrigatório"}
        if len(ms12.ID_do_Solicitante) != 20:  # 20 caracteres
            return {"status_code": 422, "detail": "M012007 - ID_do_Solicitante deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms12.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M012004 - ID_Rede_Lockers obrigatório"}
        if ms12.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms12.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M012005 - ID_Rede_Lockers inválido"}

        # gerando Data_Hora_POD
        if ms12.Data_Hora_POD is None:
            ms12.Data_Hora_POD = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # validando ID_Transacao_Unica
        if ms12.ID_Transacao_Unica is None:
            return {"status_code": 422, "detail": "M012002 - ID_Transacao_Unica obrigatório"}
        if ms12.ID_Transacao_Unica is not None:
            command_sql = f"SELECT IdTransacaoUnica from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms12.ID_Transacao_Unica}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M012001 - ID_Transacao_Unica não Existe"}


        # validando ID_da_Estacao_do_Locker
        if ms12.ID_da_Estacao_do_Locker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{ms12.ID_da_Estacao_do_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M012003 - ID_da_Estacao_do_ Locker inválido"}


        # validando versao mensageria
        if ms12.Versao_Mensageria is None:
            ms12.Versao_Mensageria = "1.0.0"

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
        idTransacaoUnica = ms12.ID_Transacao_Unica
        pod = {}
        pods = []
        dados_pod = ms12.Dados_POD
        for pod in dados_pod:
            command_sql = f"""UPDATE `reserva_encomenda_encomendas`
                                                        SET     `CopiaAssinaturaPOD` = '{pod.Codigo_Conformidade_POD}',
                                                                `DateUpdate` = now()
                                                        WHERE `IdTransacaoUnica` = '{ms12.ID_Transacao_Unica}' and `IdEncomenda` = '{pod.ID_Encomenda}';"""
            command_sql = command_sql.replace("'None'", "Null")
            command_sql = command_sql.replace("None", "Null")
            conn.execute(command_sql)

        return {"status_code": 200, "detail": "M012000 - Enviado com sucesso"}


    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms12'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS12 - Notificação de Prova de Entrega (POD)"}
