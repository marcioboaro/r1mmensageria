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
from schemas.ms13 import MS13
from cryptography.fernet import Fernet
import pika
import random
import os
import json
import requests
import logging
from rabbitmq import RabbitMQ

ms13_ms13 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()
rabbitMq = RabbitMQ()

@ms13_ms13.post("/msg/v01/lockers/order/tracking/encomenda", tags=["ms13"], description="Notificação de Eventos de Tracking de Encomenda")
def ms13(ms13: MS13, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("Notificação de Eventos de Tracking de Encomenda")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        # validando ID_do_Solicitante
        if ms13.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M013006 - ID_do_Solicitante obrigatório"}
        if len(ms13.ID_do_Solicitante) != 20:  # 20 caracteres
            return {"status_code": 422, "detail": "M013007 - ID_do_Solicitante deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms13.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M012004 - ID_Rede_Lockers obrigatório"}
        if ms13.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms13.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M012005 - ID_Rede_Lockers inválido"}

        # validando ID_Encomenda
        if ms13.ID_Encomenda is None:
            return {"status_code": 422, "detail": "M012004 - ID_Encomenda obrigatório"}

        # validando ID_Transacao_Unica
        if ms13.ID_Transacao_Unica is None:
            return {"status_code": 422, "detail": "M012002 - ID_Transacao_Unica obrigatório"}
        if ms13.ID_Transacao_Unica is not None:
            command_sql = f"SELECT IdTransacaoUnica from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms13.ID_Transacao_Unica}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M012001 - ID_Transacao_Unica não Existe"}

        # gerando Data_Hora_POD
        if ms13.Data_Hora_Notificacao_Evento_Encomenda is None:
            ms13.Data_Hora_Notificacao_Evento_Encomenda = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # validando versao mensageria
        if ms13.Versao_Mensageria is None:
            ms13.Versao_Mensageria = "1.0.0"

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
        update_tracking_reserva(ms11)

        # rotina para avaria
        if ms13.Status_Encomenda_Atual == 6 or ms13.Status_Encomenda_Atual == 11 or ms13.Status_Encomenda_Atual == 20:
            rotina_avaria(ms11, dt_string)

        elif ms13.Status_Encomenda_Atual == 7 or ms13.Status_Encomenda_Atual == 12 or ms13.Status_Encomenda_Atual == 21:
            # rotina para extravio
            rotina_extravio(ms11,dt_string) # atualização de status no webhook e envio de NS013 para shopper

        elif ms13.Status_Encomenda_Atual == 8 or ms13.Status_Encomenda_Atual == 13 or ms13.Status_Encomenda_Atual == 22:
            # rotina para roubo
            rotina_roubo(ms11,dt_string) # atualização de status no webhook e envio de NS014 para shopper

        elif ms11.Status_Encomenda_Atual == 4 or ms13.Status_Encomenda_Atual == 5 or ms13.Status_Encomenda_Atual == 9 or ms13.Status_Encomenda_Atual == 15 or ms13.Status_Encomenda_Atual == 16 or ms13.Status_Encomenda_Atual == 17 or ms13.Status_Encomenda_Atual == 18 or ms13.Status_Encomenda_Atual == 23 or ms11.Status_Reserva_Atual == 39:
            # rotina para demais atualizacoes do operador logistico
            rotina_operador(ms11,dt_string) # atualização de status no webhook

        elif ms13.Status_Encomenda_Atual == 14:
            # rotina para prorrogação de SLA
            rotina_prorrogacao_sla(ms11) # envio de lc07 (prorrogação de reserva)

        return {"status_code": 200, "detail": "M011000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms11'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS11 - Notificação de Eventos de Tracking de Reservas"}

def  update_tracking_reserva(ms13):
    try:
        command_sql = f"""UPDATE `tracking_encomenda`
                            SET     `idStatusReservaAnterior` = '{ms13.Status_Reserva_Anterior}',
                                    `idStatusReservaAtual` = '{ms13.Status_Reserva_Atual}',
                                    `DateUpdate` = now()
                            WHERE `IdTransacaoUnica` = '{ms13.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_tracking_reserva'] = sys.exc_info()
        return result


def rotina_avaria(ms13,dt_string):
    try:
        # atualizando status do pedido no webhook
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms13.ID_de_Referencia
        wb04['ID_Transacao'] = ms13.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        if ms13.Status_Reserva_Atual == 6:
            wb04['CD_Resposta'] = "WH4006 - Avaria First Mile"
        if ms13.Status_Reserva_Atual == 11:
            wb04['CD_Resposta'] = "WH4011 - Avaria CD"
        if ms13.Status_Reserva_Atual == 20:
            wb04['CD_Resposta'] = "WH4020 - Avaria Last Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms13.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        r = requests.post(url, data=json.dumps(wb04), headers={'Content-Type': 'application/json'})

        # enviando NS012 para shopper
        # abrir ocorrência

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error rotina_avaria'] = sys.exc_info()
        return result

def rotina_extravio(ms13,dt_string):
    try:
        # atualizando status do pedido no webhook
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms13.ID_de_Referencia
        wb04['ID_Transacao'] = ms13.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        if ms13.Status_Reserva_Atual == 7:
            wb04['CD_Resposta'] = "WH4007 - Extravio First Mile"
        if ms13.Status_Reserva_Atual == 12:
            wb04['CD_Resposta'] = "WH4012 - Extravio CD"
        if ms13.Status_Reserva_Atual == 21:
            wb04['CD_Resposta'] = "WH4021 - Extravio Last Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms13.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        r = requests.post(url, data=json.dumps(wb04), headers={'Content-Type': 'application/json'})

        # enviando NS013 para shopper
        # abrir ocorrência

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error rotina_extravio'] = sys.exc_info()
        return result

def rotina_roubo(ms13,dt_string):
    try:
        # atualizando status do pedido no webhook
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms13.ID_de_Referencia
        wb04['ID_Transacao'] = ms13.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        if ms13.Status_Reserva_Atual == 8:
            wb04['CD_Resposta'] = "WH4008 - Roubo First Mile"
        if ms13.Status_Reserva_Atual == 13:
            wb04['CD_Resposta'] = "WH4013 - Roubo CD"
        if ms13.Status_Reserva_Atual == 22:
            wb04['CD_Resposta'] = "WH4022 - Roubo Last Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms13.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        r = requests.post(url, data=json.dumps(wb04), headers={'Content-Type': 'application/json'})

        # enviando NS014 para shopper
        # abrir ocorrência

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error rotina_roubo'] = sys.exc_info()
        return result

def  rotina_operador(ms11,dt_string):
    try:
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_Referencia'] = ms13.ID_de_Referencia
        wb04['ID_Transacao'] = ms13.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = dt_string
        if ms13.Status_Reserva_Atual == 4:
            wb04['CD_Resposta'] = "WH4004 - Disponivel para coleta first mile no solicitante"
        if ms13.Status_Reserva_Atual == 5:
            ms13['CD_Resposta'] = "WH4005 - Transporte First Mile"
        if ms13.Status_Reserva_Atual == 9:
            wb04['CD_Resposta'] = "WH4009 - Recepção CD"
        if ms13.Status_Reserva_Atual == 15:
            wb04['CD_Resposta'] = "WH4015 - Recepção CD"
        if ms13.Status_Reserva_Atual == 16:
            wb04['CD_Resposta'] = "WH4016 - Separação CD"
        if ms13.Status_Reserva_Atual == 17:
            wb04['CD_Resposta'] = "WH4017 - Expedição CD"
        if ms13.Status_Reserva_Atual == 18:
            wb04['CD_Resposta'] = "WH4018 - Embarque Last Mile"
        if ms13.Status_Reserva_Atual == 23:
            wb04['CD_Resposta'] = "WH4023 - Entrega Encomenda no Locker"
        if ms13.Status_Reserva_Atual == 39:
            wb04['CD_Resposta'] = "WH4039 - Encomenda Armazenada CD"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms13.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        # Headers usuário e senha
        r = requests.post(url, data=json.dumps(wb04), headers={'Content-Type': 'application/json'})

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error rotina_operador'] = sys.exc_info()
        return result


def  rotina_prorrogacao_sla(ms11):
    try:
        command_sql = f"SELECT idLockerPorta, idLockerPortaFisica, idLocker from reserva_encomenda where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}'";
        record_Porta = conn.execute(command_sql).fetchone()

        # enviando pedido de prorrogação de reserva
        lc07 = {}
        lc07["CD_MSG"] = "LC07"

        content = {}
        content["ID_Referencia"] = ms11.ID_de_Referencia
        content["ID_Solicitante"] = ms11.ID_do_Solicitante
        content["ID_Rede"] = ms11.ID_Rede_Lockers
        content["ID_Transacao"] = ms11.ID_Transacao_Unica
        content["idLocker"] = record_Porta[2]
        content["AcaoExecutarPorta"] = 4
        content["idLockerPorta"] = record_Porta[0]
        content["idLockerPortaFisica"] = record_Porta[1]
        content["Versão_Software"] = "0.1"
        content["Versao_Mensageria"] = "1.0.0"

        lc07["Content"] = content

        message = json.dumps(lc07)  # Converte o dicionario em string

        rabbitMq.send_locker_queue(record_Porta[2], message)

        logger.info(sys.exc_info())

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error rotina_prorrogacao_sla'] = sys.exc_info()
        return result

