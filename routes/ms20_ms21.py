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
from schemas.ms20 import MS20, Encomendas
from cryptography.fernet import Fernet
import random
import os
import json

ms20_ms21 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

@ms20_ms21.post("/msg/v01/lockers/tag", tags=["ms20"], description="Solicitação de Geração de Etiquetas")
def ms20(ms20: MS20, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("MS20 - Solicitação de Geração de Etiquetas")
        logger.info(ms20)
        logger.info(public_id)

        # validando ID_do_Solicitante
        if ms20.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M021001 - ID_do_Solicitante obrigatório"}
        if len(ms20.ID_do_Solicitante) != 20:  # 20 caracteres
            return {"status_code": 422, "detail": "M021002 - ID_do_Solicitante deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms20.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M021003 - ID_Rede_Lockers obrigatório"}
        if ms20.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms20.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M021004 - ID_Rede_Lockers inválido"}

        # gerando Data_Hora_Solicitacao
        if ms20.Data_Hora_Solicitacao is None:
            ms20.Data_Hora_Solicitacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # validando ID_da_Estacao_Locker
        if ms20.ID_da_Estacao_Locker is None:
            return {"status_code": 422, "detail": "M021005 - ID_da_Estacao_Locker obrigatório"}
        if ms20.ID_da_Estacao_Locker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{ms20.ID_da_Estacao_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M021006 - ID_da_Estacao_Locker inválido"}
        # validando ID_Encomenda
        #if Encomendas.ID_Encomenda is None:
            #return {"status_code": 422, "detail": "M021007 - ID_Encomenda obrigatório"}
        #if Encomendas.ID_Encomenda is not None:
            #command_sql = f"SELECT IdEncomenda from reserva_encomenda_encomendas where reserva_encomenda_encomendas.IdEncomenda = '{Encomendas.ID_Encomenda}';"
            #if conn.execute(command_sql).fetchone() is None:
                #return {"status_code": 422, "detail": "M021008 - ID_Encomenda inválido"}



        # validando versao mensageria
        if ms20.Versao_Mensageria is None:
            ms20.Versao_Mensageria = "1.0.0"

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")

        ms21 = {}
        ms21['Codigo_de_MSG'] = "MS21"
        ms21['ID_de_Referencia'] = ms20.ID_de_Referencia
        ms21['ID_do_Solicitante'] = ms20.ID_do_Solicitante
        ms21['ID_Rede_Lockers'] = ms20.ID_Rede_Lockers
        ms21['ID_da_Estacao_Locker'] = ms20.ID_da_Estacao_Locker
        ms21['Codigo_Resposta_MS21'] = 'M021000 - Sucesso'
        ms21['Data_Hora_Resposta'] = dt_string
        ms21['ID_Transacao_Unica'] = ms20.ID_Transacao_Unica
        encomenda = {}
        encomendas = []
        info_encomendas = ms20.Info_Encomendas
        for encomenda in info_encomendas:
            enc_temp = {}
            enc_temp['ID_Encomenda'] = encomenda.ID_Encomenda
            enc_temp['Tipo_de_Servico_Reserva'] = encomenda.Tipo_de_Servico_Reserva
            command_sql = f"""SELECT EncomendaEtiqueta
                                        FROM `rede1minuto`.`reserva_encomenda_encomendas`
                                        where reserva_encomenda_encomendas.IdEncomenda = '{encomenda.ID_Encomenda}'
                                        and IdTransacaoUnica = '{ms20.ID_Transacao_Unica}';"""
            record_encomenda = conn.execute(command_sql).fetchone()
            enc_temp['Etiqueta_Encomenda_Rede1minuto'] = record_encomenda[0]
            encomendas.append(enc_temp)
        ms21['Info_Encomendas'] = encomendas
        ms21['Versao_Mensageria'] = ms20.Versao_Mensageria
        return ms21
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms20'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS21 - Solicitação de Geração de Etiquetas"}


