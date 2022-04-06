# -*- coding: utf-8 -*-

from typing import Any
from sqlalchemy import create_engine
from json import dumps
import logging
import traceback
import sys
import uuid  # for public id
from datetime import datetime, timedelta
from functools import wraps
import ast
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from config.db import conn
from config.log import logger
from auth.auth import AuthHandler
from schemas.ms14Simplified import MS14Simplified
from cryptography.fernet import Fernet
from config.log import logger
import pika
import sys
import os
import json

ms14_ms15 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()

@ms14_simplified.post("/msg/v01/lockers/order/status2", tags=["ms14s"], description="Consulta de Status de Encomendas Designadas - Simplificado - Logistica")
def ms14_simplified(ms14s: MS14Simplified, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("Consulta de Status de Encomendas Designadas - Logistica")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        # validando ID_do_Solicitante
        if ms14s.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M012006 - ID_do_Solicitante_Designado obrigatório"}
        if len(ms14s.ID_do_Solicitante_Designado) != 20:  # 20 caracteres
            return {"status_code": 422, "detail": "M012007 - ID_do_Solicitante_Designado deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms14s.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M012004 - ID_Rede_Lockers obrigatório"}
        if ms14s.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms14s.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M012005 - ID_Rede_Lockers inválido"}

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
        where = 0
        ms15s = {}
        ms15s['Codigo_de_MSG'] = "MS15Simplified"
        ms15s['ID_de_Referencia'] = ""
        ms15s['ID_do_Solicitante'] = ms14s.ID_do_Solicitante
        ms15s['ID_Rede_Lockers'] = ms14s.ID_Rede_Lockers
        ms15s['Codigo_Resposta_MS15'] = 'M015000 - Sucesso'
        ms15s['Data_Hora_Resposta'] = dt_string

        command_sql = f"""SELECT `reserva_encomenda`.`IdTransacaoUnica`,
                                `reserva_status`.`StatusReservaDescricao`,
                                `reserva_encomenda`.`idPSLDesignado`,
                                `locker`.`idPais`,
                                `locker`.`LockerCidade`,
                                `locker`.`cep`,
                                `locker`.`LockerBairro`,
                                `locker`.`LockerEndereco`,
                                `locker`.`LockerNumero`,
                                `locker`.`LockerComplemento`,
                                `locker`.`idOperadoresLogistico`,
                                `locker`.`idLocker`,
                                `reserva_encomenda`.`DataHoraInicioReserva`,
                                `reserva_encomenda`.`DataHoraFinalReserva`,
                                `reserva_tipo_servico`.`ServicoReservaTipo`,
                                Count(encomendas.IdEncomenda)
                        FROM `rede1minuto`.`reserva_encomenda`
                        INNER JOIN `reserva_status` ON (`reserva_encomenda`.`idStatusEncomenda` = `reserva_status`.`idStatusReserva`)
                        INNER JOIN `locker` ON (`reserva_encomenda`.`idLocker` = `locker`.`idLocker`)
                        INNER JOIN `encomendas` ON (`reserva_encomenda`.`IdTransacaoUnica` = `encomendas`.`IdTransacaoUnica`)
                        INNER JOIN `reserva_tipo_servico` ON (`reserva_encomenda`.`idServicoReserva` = `reserva_tipo_servico`.`idServicoReserva`)"""

        if ms14s.ID_Rede_Lockers is not None:
            command_sql += f" and `reserva_encomenda`.`idRede` = '{ms14s.ID_Rede_Lockers}'"
        if ms14s.ID_do_Solicitante is not None:
            command_sql += f" and `reserva_encomenda`.`ID_Solicitante` = '{ms14s.ID_do_Solicitante}'"
        command_sql += f" group by `reserva_encomenda`.`IdTransacaoUnica`"
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        records = conn.execute(command_sql).fetchall()
        reservas = []
        for row in records:
            reserva = {}
            reserva['ID_Transacao_Unica'] = row[0]
            reserva['Status_Reserva'] = row[1]
            reserva['ID_PSL_Designado'] = row[2]
            reserva['Data_Hora_Designacao'] = dt_string
            reserva['Codigo_Pais_Locker'] = row[3]
            reserva['Cidade_Locker'] = row[4]
            reserva['CEP_Locker'] = row[5]
            reserva['Bairro_Locker'] = row[6]
            reserva['Endereco_Locker'] = row[7]
            reserva['Numero_Endereco_Locker'] = row[8]
            reserva['Complemento_Locker'] = row[9]
            reserva['ID_do_Operador_do_Locker'] = row[10]
            reserva['ID_da_Estacao_do_Locker'] = row[11]
            reserva['DataHora_Inicio_Reserva'] = row[12]
            reserva['DataHora_Final_Reserva'] = row[13]
            reserva['Tipo_de_Servico'] = row[14]
            reserva['Contador_de_Encomendas_por_Designacao'] = row[15]
            reservas.append(reserva)
        for reserva_encomenda_encomendas in records:
            command_sql = f"""SELECT `encomendas`.`IdTransacaoUnica`, 
                                    `encomendas`.`IdEncomenda`,
                                    `ShopperMobileNumero`,
                                    `ShopperEmail`,
                                    `idShopperCPF_CNPJ`,
                                    `ShopperMoeda`,
                                    `ShopperMobileNumero`,
                                    `ShopperValorEncomenda`,
                                    `ShopperNotaFiscal`,
                                    `encomendas`.`idPais`,
                                    `ShopperCidade`,
                                    `encomendas`.`cep`,
                                    `ShopperBairro`,
                                    `ShopperEndereco`,
                                    `ShopperNumero`,
                                    `ShopperComplemento`,
                                    `CodigoRastreamentoEncomenda`,
                                    `CodigoBarrasConteudoEncomenda`,
                                    `DescricaoConteudoEncomenda`,
                                    `ShopperEndereco`,
                                    `ShopperNumero`,
                                    `ShopperComplemento`,
                                    `CodigoRastreamentoEncomenda`,
                                    `CodigoBarrasConteudoEncomenda`
                                    FROM `rede1minuto`.`encomendas`
                                    LEFT JOIN `reserva_encomenda` ON (`encomendas`.`IdTransacaoUnica` = `reserva_encomenda`.`IdTransacaoUnica`)
                                    LEFT JOIN `locker` ON (`reserva_encomenda`.`idLocker` = `locker`.`idLocker`)
                                    where encomendas.IdTransacaoUnica = '{reserva_encomenda_encomendas[0]}'"""
            command_sql = command_sql.replace("'None'", "Null")
            command_sql = command_sql.replace("None", "Null")
            records0 = conn.execute(command_sql).fetchall()
            encomendas = []
            for row in records0:
                encomenda = {}
                encomenda['ID_Encomenda'] = row[1]
                encomenda['Numero_Mobile_Shopper'] = row[2]
                encomenda['Endereco_de_Email_do_Shopper'] = row[3]
                encomenda['CPF_CNPJ_Shopper'] = row[4]
                encomenda['Moeda_Shopper'] = row[5]
                encomenda['Valor_Encomenda_Shopper'] = row[6]
                encomenda['Numero_Nota_Fiscal_Encomenda_Shopper'] = row[7]
                encomenda['Codigo_Pais_Shopper'] = row[8]
                encomenda['Cidade_Shopper'] = row[9]
                encomenda['CEP_Shopper'] = row[10]
                encomenda['Bairro_Shopper'] = row[11]
                encomenda['Endereco_Shopper'] = row[12]
                encomenda['Numero_Shopper'] = row[13]
                encomenda['Complemento_Shopper'] = row[14]
                encomenda['Codigo_Rastreamento_Encomenda'] = row[15]
                encomenda['Codigo_Barras_Conteudo_Encomenda'] = row[16]
                encomenda['Descricao_Conteudo_Encomenda'] = row[17]
                encomendas.append(encomenda)
            for reserva in reservas:
                if reserva['ID_Transacao_Unica'] == reserva_encomenda_encomendas[0]:
                    reserva['Info_Encomendas_por_Designacao'] = encomendas
        ms15s['Info_Total_de_Encomendas_Designadas'] = reservas
        return ms15s
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms14Simplified'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS14Simplified - Consulta de Status de Encomendas Designadas - Logistica"}