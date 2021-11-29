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
from schemas.ms09 import MS09
from cryptography.fernet import Fernet
import random
import os
import json

ms09_ms10 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

# @ms07_ms08.post("/ms05", tags=["ms08"], response_model=MS08, description="Cancelamento de reserva")
@ms09_ms10.post("/msg/v01/lockers/qrcode", tags=["ms09"], description="Solicitação para gerar QRCode")
def ms09(ms09: MS09, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("MS09 - Solicitação para gerar QRCode")
        logger.info(ms09)
        logger.info(public_id)

        # validando ID_do_Solicitante
        if ms09.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M010006 - ID_do_Solicitante obrigatório"}
        if len(ms09.ID_do_Solicitante) != 20: # 20 caracteres
            return {"status_code": 422, "detail": "M010011 - ID_do_Solicitante deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms09.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M010015 - ID_Rede_Lockers obrigatório"}
        if ms09.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms09.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M010015 - ID_Rede_Lockers inválido"}

        # validando ID_Encomenda
        if ms09.ID_Encomenda is not None:
            command_sql = f"SELECT IdEncomenda from reserva_encomenda_encomendas where reserva_encomenda_encomendas.IdEncomenda = '{ms09.ID_Encomenda}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M010018 - ID_Encomenda inválido"}

        # gerando Tipo_de_serviço_abertura_porta
        if ms09.Tipo_de_servico_abertura_porta is None:
            return {"status_code": 422, "detail": "M010009 - Tipo_de_servico_abertura_porta obrigatório"}

        # gerando Data_Hora_Solicitacao
        if ms09.Data_Hora_Solicitacao is None:
            ms09.Data_Hora_Solicitacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # validando mensagem "Reserva não Existe"
        if ms09.ID_Transacao_Unica is None:
            return {"status_code": 422, "detail": "M010008 - ID_Transacao_Unica obrigatório"}
        if ms09.ID_Transacao_Unica is not None:
            command_sql = f"SELECT IdTransacaoUnica from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms09.ID_Transacao_Unica}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M010001 - Reserva não Existe"}

        # validando versao mensageria
        if ms09.Versao_Mensageria is None:
            ms09.Versao_Mensageria = "1.0.0"

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")

        command_sql = f"""SELECT `reserva_encomenda`.`QRCODE`,
                                    `reserva_encomenda`.`CodigoAberturaPorta`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms09.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()

        ms10 = {}
        ms10['Codigo_de_MSG'] = "MS10"
        ms10['ID_de_Referencia'] = ms09.ID_de_Referencia
        ms10['ID_do_Solicitante'] = ms09.ID_do_Solicitante
        ms10['ID_Rede_Lockers'] = ms09.ID_Rede_Lockers
        ms10['Codigo_Resposta_MS10'] = 'M010000 - Sucesso'
        ms10['ID_Transacao_Unica'] = ms09.ID_Transacao_Unica
        ms10['ID_Encomenda'] = ms09.ID_Encomenda
        ms10['ID_Geracao_QRCODE'] = record[0]
        ms10['CodigoAberturaPorta'] = record[1]
        ms10['Data_Hora_Resposta'] = dt_string
        ms10['Versao_Mensageria'] = ms09.Versao_Mensageria
        return ms10
    except Exception as e:
        logger.error(e)
        logger.info("MS09 - Solicitação para gerar QRCode")
        return {"status_code": 500, "detail": "MS09 - Solicitação para gerar QRCode"}


