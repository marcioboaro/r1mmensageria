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
import requests
import logging

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
            now = datetime.now() - timedelta(hours=3)
            dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
            ms11.Data_Hora_Notificacao_Evento_Reserva = dt_string

        # validando versao mensageria
        if ms11.Versao_Mensageria is None:
            ms11.Versao_Mensageria = "1.0.0"

        now = datetime.now() - timedelta(hours=3)
        dt_string = now.strftime('%Y-%m-%d %H:%M:%S')

        update_tracking_reserva(ms11)

        if ms11.Status_Reserva_Atual == {4}:
            update_wh04_WH4004(ms11)
        if ms11.Status_Reserva_Atual == {5}:
            update_wh04_WH4005(ms11)
        if ms11.Status_Reserva_Atual == {6}:
            update_wh04_WH4006(ms11)
        if ms11.Status_Reserva_Atual == {7}:
            update_wh04_WH4007(ms11)
        if ms11.Status_Reserva_Atual == {8}:
            update_wh04_WH4008(ms11)
        if ms11.Status_Reserva_Atual == {9}:
            update_wh04_WH4009(ms11)
        if ms11.Status_Reserva_Atual == {11}:
            update_wh04_WH4011(ms11)
        if ms11.Status_Reserva_Atual == {12}:
            update_wh04_WH4012(ms11)
        if ms11.Status_Reserva_Atual == {13}:
            update_wh04_WH4013(ms11)
        if ms11.Status_Reserva_Atual == {14}:
            update_wh04_WH4014(ms11)
        if ms11.Status_Reserva_Atual == {15}:
            update_wh04_WH4015(ms11)
        if ms11.Status_Reserva_Atual == {16}:
            update_wh04_WH4016(ms11)
        if ms11.Status_Reserva_Atual == {17}:
            update_wh04_WH4017(ms11)
        if ms11.Status_Reserva_Atual == {18}:
            update_wh04_WH4018(ms11)
        if ms11.Status_Reserva_Atual == {20}:
            update_wh04_WH4020(ms11)
        if ms11.Status_Reserva_Atual == {21}:
            update_wh04_WH4021(ms11)
        if ms11.Status_Reserva_Atual == {22}:
            update_wh04_WH4022(ms11)

        return {"status_code": 200, "detail": "M011000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms11'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS11 - Notificação de Eventos de Tracking de Reservas"}

def  update_tracking_reserva(ms11):
    try:
        command_sql = f"""UPDATE `tracking_encomenda`
                                        SET     `idStatusEncomendaAnterior` = '{ms11.Status_Reserva_Anterior}',
                                                `idStatusEncomendaAtual` = '{ms11.Status_Reserva_Atual}',
                                                `DateUpdate` = now()
                                        WHERE `IdTransacaoUnica` = '{ms11.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_tracking_reserva'] = sys.exc_info()
        return result


def  update_wh04_WH4004(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4004 - Disponível para Coleta First Mile no Solicitante"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4004'] = sys.exc_info()
        return result

def  update_wh04_WH4005(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4005 - Transporte First Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4005'] = sys.exc_info()
        return result


def  update_wh04_WH4006(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4006 - Avaria First Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4006'] = sys.exc_info()
        return result


def  update_wh04_WH4007(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4007 - Extravio First Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4007'] = sys.exc_info()
        return result

def  update_wh04_WH4008(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4008 - Roubo First Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4008'] = sys.exc_info()
        return result


def  update_wh04_WH4009(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4009 - Recepção CD"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4009'] = sys.exc_info()
        return result

def  update_wh04_WH4011(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4011 - Avaria CD"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4011'] = sys.exc_info()
        return result

def  update_wh04_WH4012(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4012 - Extravio CD"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4012'] = sys.exc_info()
        return result

def  update_wh04_WH4013(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4013 - Roubo CD"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4013'] = sys.exc_info()
        return result

def  update_wh04_WH4014(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4014 - Prorrogação  SLA"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4014'] = sys.exc_info()
        return result

def  update_wh04_WH4015(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4015 - Recepção CD"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4015'] = sys.exc_info()
        return result

def  update_wh04_WH4016(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4016 - Separação CD"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4016'] = sys.exc_info()
        return result

def  update_wh04_WH4017(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4017 - Expedição CD"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4017'] = sys.exc_info()
        return result

def  update_wh04_WH4018(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4018 - Embarque Last Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4018'] = sys.exc_info()
        return result

def  update_wh04_WH4020(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4020 - Avaria Last Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4020'] = sys.exc_info()
        return result

def  update_wh04_WH4021(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4021 - Extravio Last Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4021'] = sys.exc_info()
        return result

def  update_wh04_WH4022(ms11):
    try:
        command_sql = f"""SELECT `tracking_encomenda`.`idStatusReservaAtual`
                                    FROM `rede1minuto`.`tracking_encomenda`
                                    where tracking_encomenda.idTransacao = '{ms11.ID_Transacao_Unica}';"""
        reserva = conn.execute(command_sql).fetchone()
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        wb04['CD_Resposta'] = "WH4022 - Roubo Last Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        response = requests.request("POST", url, json=wb04, headers=headers)
        parsed = json.loads(response.content)
        pretty = json.dumps(parsed, indent=4, sort_keys=True)
        print(pretty)

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_wh04_WH4022'] = sys.exc_info()
        return result