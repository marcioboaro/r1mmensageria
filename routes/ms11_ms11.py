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

        now = datetime.now()

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

        # gerando Data_Hora
        if ms11.Data_Hora_Notificacao_Evento_Reserva is None:
            ms11.Data_Hora_Notificacao_Evento_Reserva = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # validando versao mensageria
        if ms11.Versao_Mensageria is None:
            ms11.Versao_Mensageria = "1.0.0"

        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
        update_tracking_reserva(ms11)

        # ataulização de status de reserva/encomenda
        update_reserva_encomenda(ms11)

        # rotina para avaria
        if ms11.Status_Reserva_Atual == 6 or ms11.Status_Reserva_Atual == 11 or ms11.Status_Reserva_Atual == 20:
            rotina_avaria(ms11)

        elif ms11.Status_Reserva_Atual == 7 or ms11.Status_Reserva_Atual == 12 or ms11.Status_Reserva_Atual == 21:
            # rotina para extravio
            rotina_extravio(ms11) # atualização de status no webhook e envio de NS013 para shopper

        elif ms11.Status_Reserva_Atual == 8 or ms11.Status_Reserva_Atual == 13 or ms11.Status_Reserva_Atual == 22:
            # rotina para roubo
            rotina_roubo(ms11) # atualização de status no webhook e envio de NS014 para shopper

        elif ms11.Status_Reserva_Atual == 4 or ms11.Status_Reserva_Atual == 5 or ms11.Status_Reserva_Atual == 9 or ms11.Status_Reserva_Atual == 15 or ms11.Status_Reserva_Atual == 16 or ms11.Status_Reserva_Atual == 17 or ms11.Status_Reserva_Atual == 18 or ms11.Status_Reserva_Atual == 23 or ms11.Status_Reserva_Atual == 39:
            # rotina para demais atualizacoes do operador logistico
            rotina_operador(ms11) # atualização de status no webhook

        elif ms11.Status_Reserva_Atual == 14:
            # rotina para prorrogação de SLA
            rotina_prorrogacao_sla(ms11) # envio de lc07 (prorrogação de reserva)
            rotina_operador(ms11)

        ###################### teste no webhook a ser retirado posteriormente ###############################
        elif ms11.Status_Reserva_Atual == 24 or ms11.Status_Reserva_Atual == 25 or ms11.Status_Reserva_Atual == 28 or ms11.Status_Reserva_Atual == 29 or ms11.Status_Reserva_Atual == 30 or ms11.Status_Reserva_Atual == 31 or ms11.Status_Reserva_Atual == 32 or ms11.Status_Reserva_Atual == 33 or ms11.Status_Reserva_Atual == 34 or ms11.Status_Reserva_Atual == 35 or ms11.Status_Reserva_Atual == 36 or ms11.Status_Reserva_Atual == 37 or ms11.Status_Reserva_Atual == 38 or ms11.Status_Reserva_Atual == 40 or ms11.Status_Reserva_Atual == 41:
            rotina_teste(ms11)
        ###################### teste no webhook a ser retirado posteriormente ###############################

        return {"status_code": 200, "detail": "M011000 - Enviado com sucesso"}
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms11'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS11 - Notificação de Eventos de Tracking de Reservas"}


def update_reserva_encomenda(ms11):
    try:

        command_sql = f"""UPDATE `reserva_encomenda`
                                            SET     `idStatusReserva` = '{ms11.Status_Reserva_Atual}'
                                            WHERE `IdTransacaoUnica` = '{ms11.ID_Transacao_Unica}';"""
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error update_reserva_encomenda'] = sys.exc_info()
        return result

def  update_tracking_reserva(ms11):
    try:

        command_sql = f"""UPDATE `tracking_encomenda`
                            SET     `idStatusReservaAnterior` = '{ms11.Status_Reserva_Anterior}',
                                    `idStatusReservaAtual` = '{ms11.Status_Reserva_Atual}'
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

###################### teste no webhook a ser retirado posteriormente ###############################
def  rotina_teste(ms11):
    try:
        # atualizando status do pedido no webhook
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_de_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao_Unica'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if ms11.Status_Reserva_Atual == 24:
            wb04['CD_Resposta'] = "WH4024 - Encomenda Aguardando Retirada no Locker"
        if ms11.Status_Reserva_Atual == 25:
            wb04['CD_Resposta'] = "WH4025 - Retirada Shopper"
        if ms11.Status_Reserva_Atual == 28:
            wb04['CD_Resposta'] = "WH4028 - Coleta não retirada pelo Shopper por falha operacional"
        if ms11.Status_Reserva_Atual == 29:
            wb04['CD_Resposta'] = "WH4029 - Entrega Express no destinatário por falha operacional"
        if ms11.Status_Reserva_Atual == 30:
            wb04['CD_Resposta'] = "WH4030 - Vandalismo Locker com perda de encomenda"
        if ms11.Status_Reserva_Atual == 31:
            wb04['CD_Resposta'] = "WH4031 - SLA Vencido e Encomenda não retirada pela REDE"
        if ms11.Status_Reserva_Atual == 32:
            wb04['CD_Resposta'] = "WH4032 - Coleta de Encomenda não retirada SLA pelo Shopper"
        if ms11.Status_Reserva_Atual == 33:
            wb04['CD_Resposta'] = "WH4033 - Entrega Express no destinatário por solicitação Shopper ou Mktplace"
        if ms11.Status_Reserva_Atual == 34:
            wb04['CD_Resposta'] = "WH4034 - Deposito de Encomenda não realizado pelo Shopper na Devolução"
        if ms11.Status_Reserva_Atual == 35:
            wb04['CD_Resposta'] = "WH4035 - Deposito de Encomenda não realizada pelo E-Commece na Coleta (Locker to Locker)"
        if ms11.Status_Reserva_Atual == 36:
            wb04['CD_Resposta'] = "WH4036 - Deposito de Encomenda não realizado Locker Off ( Locker to Locker)"
        if ms11.Status_Reserva_Atual == 37:
            wb04['CD_Resposta'] = "WH4037 - Coleta Express efetuada no Destinatário (Locker to Locker) por problema operacional"
        if ms11.Status_Reserva_Atual == 38:
            wb04['CD_Resposta'] = "WH4038 - Coleta efetuada com sucesso em encomenda depositada pelo E Commerce (Locker to Locker)"
        if ms11.Status_Reserva_Atual == 40:
            wb04['CD_Resposta'] = "WH4040 - Reserva sem encomenda expira em 24 horas"
        if ms11.Status_Reserva_Atual == 41:
            wb04['CD_Resposta'] = "WH4041 - Reserva com encomenda expira em 24 horas"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
        record = conn.execute(command_sql).fetchone()
        logger.warning(command_sql)
        url = record[0]

        r = requests.post(url, data=json.dumps(wb04), headers={'Content-Type': 'application/json'})

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error rotina_avaria'] = sys.exc_info()
        return result

######################## teste no webhook a ser retirado posteriormente ###############################




def rotina_avaria(ms11):
    try:
        # atualizando status do pedido no webhook
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_de_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao_Unica'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if ms11.Status_Reserva_Atual == 6:
            wb04['CD_Resposta'] = "WH4006 - Avaria First Mile"
        if ms11.Status_Reserva_Atual == 11:
            wb04['CD_Resposta'] = "WH4011 - Avaria CD"
        if ms11.Status_Reserva_Atual == 20:
            wb04['CD_Resposta'] = "WH4020 - Avaria Last Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
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


def rotina_extravio(ms11):
    try:
        # atualizando status do pedido no webhook
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_de_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao_Unica'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if ms11.Status_Reserva_Atual == 7:
            wb04['CD_Resposta'] = "WH4007 -  Extravio First Mile"
        if ms11.Status_Reserva_Atual == 12:
            wb04['CD_Resposta'] = "WH4012 - Extravio CD"
        if ms11.Status_Reserva_Atual == 21:
            wb04['CD_Resposta'] = "WH4021 - Extravio Last Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
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



def rotina_roubo(ms11):
    try:
        # atualizando status do pedido no webhook
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_de_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao_Unica'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if ms11.Status_Reserva_Atual == 8:
            wb04['CD_Resposta'] = "WH4008 - Roubo First Mile"
        if ms11.Status_Reserva_Atual == 13:
            wb04['CD_Resposta'] = "WH4013 - Roubo CD"
        if ms11.Status_Reserva_Atual == 22:
            wb04['CD_Resposta'] = "WH4022 - Roubo Last Mile"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
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

def  rotina_operador(ms11):
    try:
        wb04 = {}
        wb04['CD_MSG'] = "WH004"
        wb04['ID_de_Referencia'] = ms11.ID_de_Referencia
        wb04['ID_Transacao_Unica'] = ms11.ID_Transacao_Unica
        wb04['Data_Hora_Resposta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if ms11.Status_Reserva_Atual == 4:
            wb04['CD_Resposta'] = "WH4004 - Disponivel para coleta first mile no solicitante"
        if ms11.Status_Reserva_Atual == 5:
            wb04['CD_Resposta'] = "WH4005 - Transporte First Mile"
        if ms11.Status_Reserva_Atual == 9:
            wb04['CD_Resposta'] = "WH4009 - Recepção CD"
        if ms11.Status_Reserva_Atual == 15:
            wb04['CD_Resposta'] = "WH4015 - Recepção CD"
        if ms11.Status_Reserva_Atual == 16:
            wb04['CD_Resposta'] = "WH4016 - Separação CD"
        if ms11.Status_Reserva_Atual == 17:
            wb04['CD_Resposta'] = "WH4017 - Expedição CD"
        if ms11.Status_Reserva_Atual == 18:
            wb04['CD_Resposta'] = "WH4018 - Embarque Last Mile"
        if ms11.Status_Reserva_Atual == 23:
            wb04['CD_Resposta'] = "WH4023 - Entrega Encomenda no Locker"
        if ms11.Status_Reserva_Atual == 39:
            wb04['CD_Resposta'] = "WH4039 - Encomenda Armazenada CD"
        if ms11.Status_Reserva_Atual == 14:
            wb04['CD_Resposta'] = "WH4014 - Prorrogação SLA"

        command_sql = f"""SELECT `reserva_encomenda`.`URL_CALL_BACK`
                                FROM `rede1minuto`.`reserva_encomenda`
                                where reserva_encomenda.IdTransacaoUnica = '{ms11.ID_Transacao_Unica}';"""
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
        content["ID_Transacao_Unica"] = ms11.ID_Transacao_Unica
        content["idLocker"] = record_Porta[3]
        content["AcaoExecutarPorta"] = 4
        content["idLockerPorta"] = record_Porta[0]
        content["idLockerPortaFisica"] = record_Porta[1]
        content["Versão_Software"] = "0.1"
        content["Versao_Mensageria"] = "1.0.0"

        lc07["Content"] = content

        MQ_Name = 'Rede1Min_MQ'
        URL = 'amqp://rede1min:Minuto@167.71.26.87'  # URL do RabbitMQ
        queue_name = record_Porta[3] + '_locker_output'  # Nome da fila do RabbitMQ

        url = os.environ.get(MQ_Name, URL)
        params = pika.URLParameters(url)
        params.socket_timeout = 6

        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        message = json.dumps(lc07)  # Converte o dicionario em string

        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

        connection.close()
        logger.info(sys.exc_info())

    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error rotina_prorrogacao_sla'] = sys.exc_info()
        return result

