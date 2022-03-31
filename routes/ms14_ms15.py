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
from schemas.ms14 import MS14
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

@ms14_ms15.post("/msg/v01/lockers/order/status", tags=["ms14"], description="Consulta de Status de Encomendas Designadas - Logistica")
def ms14(ms14: MS14, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("Consulta de Status de Encomendas Designadas - Logistica")
        logger.info(f"Usuário que fez a solicitação: {public_id}")

        # validando ID_do_Solicitante_Designado
        if ms14.ID_do_Solicitante_Designado is None:
            return {"status_code": 422, "detail": "M012006 - ID_do_Solicitante_Designado obrigatório"}
        if len(ms14.ID_do_Solicitante_Designado) != 20:  # 20 caracteres
            return {"status_code": 422, "detail": "M012007 - ID_do_Solicitante_Designado deve conter 20 caracteres"}

        # validando ID_do_Solicitante_Designador
        if ms14.ID_do_Solicitante_Designador is None:
            return {"status_code": 422, "detail": "M012006 - ID_do_Solicitante_Designador obrigatório"}
        if len(ms14.ID_do_Solicitante_Designador) != 20:  # 20 caracteres
            return {"status_code": 422, "detail": "M012007 - ID_do_Solicitante_Designador deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms14.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M012004 - ID_Rede_Lockers obrigatório"}
        if ms14.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms14.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M012005 - ID_Rede_Lockers inválido"}

        # validando ID_TICKET_Ocorrencia_Encomenda
        if ms14.ID_TICKET_Ocorrencia_Encomenda is not None:
            command_sql = f"SELECT IdEncomenda from encomendas where encomendas.IdEncomenda = '{ms14.ID_TICKET_Ocorrencia_Encomenda}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M014001 - ID_TICKET_Ocorrencia_Encomenda não Existe"}

        # validando Codigo_Pais_Locker
#        if ms14.Codigo_Pais_Locker is not None:
#            command_sql = f"SELECT idPais from locker where locker.idPais = '{ms14.Codigo_Pais_Locker}';"
#            if conn.execute(command_sql).fetchone() is None:
#                return {"status_code": 422, "detail": "M014001 - Codigo_Pais_Locker não Existe"}

        if ms14.DataHora_Inicio_Consuta_Encomendas_Designadas is None:
            return {"status_code": 422, "detail": "M014004 - DataHora_Inicio_Consuta_Encomendas_Designadas obrigatório"}

        if ms14.DataHora_Final_Consuta_Encomendas_Designadas is None:
            return {"status_code": 422, "detail": "M014004 - DataHora_Final_Consuta_Encomendas_Designadas obrigatório"}

        # validando Cidade_Locker
        if ms14.Cidade_Locker is not None:
            command_sql = f"SELECT LockerCidade from locker where locker.LockerCidade = '{ms14.Cidade_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M014001 - Cidade_Locker não Existe"}

        # gerando Data_Hora_Solicitacao
        if ms14.Data_Hora_Solicitacao is None:
            ms14.Data_Hora_Solicitacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # validando versao mensageria
        if ms14.Versao_Mensageria is None:
            ms14.Versao_Mensageria = "1.0.0"

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
        where = 0
        ms15 = {}
        ms15['Codigo_de_MSG'] = "MS15"
        ms15['ID_de_Referencia'] = ms14.ID_de_Referencia
        ms15['ID_do_Solicitante_Designado'] = ms14.ID_do_Solicitante_Designado
        ms15['ID_Rede_Lockers'] = ms14.ID_Rede_Lockers
        ms15['ID_do_Solicitante_Designador'] = ms14.ID_do_Solicitante_Designador
        ms15['Codigo_Resposta_MS15'] = 'M015000 - Sucesso'
        ms15['Data_Hora_Resposta'] = dt_string

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
                                Count(reserva_encomenda_encomendas.IdEncomenda)
                        FROM `rede1minuto`.`reserva_encomenda`
                        INNER JOIN `reserva_status` ON (`reserva_encomenda`.`idStatusEncomenda` = `reserva_status`.`idStatusReserva`)
                        INNER JOIN `locker` ON (`reserva_encomenda`.`idLocker` = `locker`.`idLocker`)
                        INNER JOIN `reserva_tipo_servico` ON (`reserva_encomenda`.`idServicoReserva` = `reserva_tipo_servico`.`idServicoReserva`)"""
#                        INNER JOIN `reserva_encomenda_encomendas` ON (`reserva_encomenda`.`IdTransacaoUnica` = `reserva_encomenda_encomendas`.`IdTransacaoUnica`)

        if ms14.DataHora_Inicio_Consuta_Encomendas_Designadas and ms14.DataHora_Final_Consuta_Encomendas_Designadas is not None:
            command_sql += f" and reserva_encomenda.DateAt BETWEEN '{ms14.DataHora_Inicio_Consuta_Encomendas_Designadas}' AND '{ms14.DataHora_Final_Consuta_Encomendas_Designadas}'"
        if ms14.Codigo_Pais_Locker is not None:
            command_sql += f" and `locker`.`idPais` = '{ms14.Codigo_Pais_Locker}'"
        if ms14.Cidade_Locker is not None:
            command_sql += f" and `locker`.`LockerCidade` = '{ms14.Cidade_Locker}'"
        if ms14.ID_TICKET_Ocorrencia_Encomenda is not None:
            command_sql += f" and `reserva_encomenda_encomendas`.`IdEncomenda` = '{ms14.ID_TICKET_Ocorrencia_Encomenda}'"
        if ms14.ID_Rede_Lockers is not None:
            command_sql += f" and `reserva_encomenda`.`idRede` = '{ms14.ID_Rede_Lockers}'"
        command_sql += f" group by `reserva_encomenda`.`IdTransacaoUnica`"
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        logger.warning("Primeiro Select MS14: " + command_sql)
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
            logger.warning("Segundo Select MS14: " + command_sql)
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
        ms15['Info_Total_de_Encomendas_Designadas'] = reservas
        ms15['Versao_Mensageria'] = ms14.Versao_Mensageria
        return ms15
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms14'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS14 - Consulta de Status de Encomendas Designadas - Logistica"}
