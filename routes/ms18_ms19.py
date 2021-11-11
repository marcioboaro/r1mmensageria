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
from schemas.ms18 import MS18
from cryptography.fernet import Fernet
import random
import os
import json

ms18_ms19 = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)
auth_handler = AuthHandler()


# Consulta catalogo Lockers
def latlong_valid(latlong):
    try:
        ll = latlong.split(" ")
        lat = float(ll[0])
        lon = float(ll[1])
        if lat >= -90.0 and lat <= 90.0 and lon >= -180.0 and lon <= 180.0:
            return True
        else:
            return False
    except:
        return False


@ms18_ms19post("/msg/v01/lockers/slot/rent", tags=["ms18"], description="Solicitação de Locação de Porta em Locker")
def ms18(ms18: MS18, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("MS18 - Solicitação de Locação de Porta em Locker")
        logger.info(ms18)
        logger.info(public_id)

        # validando ID_do_Solicitante
        if ms18.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M010006 - ID_do_Solicitante obrigatório"}
        if len(ms18.ID_do_Solicitante) != 20: # 20 caracteres
            return {"status_code": 422, "detail": "M010011 - ID_do_Solicitante deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms18.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M010015 - ID_Rede_Lockers obrigatório"}
        if ms18.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms18.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M010015 - ID_Rede_Lockers inválido"}

        # gerando Data_Hora_Solicitacao
        if ms18.Data_Hora_Solicitacao is None:
            ms18.Data_Hora_Solicitacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # validando ID_da_Estacao_do_Locker
        if ms18.ID_da_Estacao_do_Locker is None:
            return {"status_code": 422, "detail": "M010015 - ID_da_Estacao_do_Locker obrigatório"}
        if ms18.ID_da_Estacao_do_Locker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{ms09.ID_da_Estacao_do_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M06023 - ID_da_Estacao_do_ Locker inválido"}

        # validando Categoria_Porta
        if ms18.Categoria_Porta is None:
            return {"status_code": 422, "detail": "M010008 - Categoria_Porta obrigatório"}
        if ms18.Categoria_Porta is not None:
            command_sql = f"SELECT idLockerPortaCategoria from locker_porta_categoria where locker_porta_categoria.idLockerPortaCategoria = '{ms18.Categoria_Porta}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M06023 - Categoria_Porta inválido"}

        # validando versao mensageria
        if ms18.Versao_Mensageria is None:
            ms18.Versao_Mensageria = "1.0.0"

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")

        ms19 = {}
        ms19['Codigo_de_MSG'] = "MS19"
        ms19['ID_de_Referencia'] = ms18.ID_de_Referencia
        ms19['ID_do_Solicitante'] = ms18.ID_do_Solicitante
        ms19['ID_Rede_Lockers'] = ms18.ID_Rede_Lockers
        ms19['ID_da_Estacao_do_Locker'] = ms18.ID_da_Estacao_do_Locker

        command_sql = f"""SELECT idLockerPorta,
                                    idLockerPortaFisica,
                                    FROM `rede1minuto`.`locker_porta`
                                    where locker_porta.idLocker = '{ms18.ID_da_Estacao_do_Locker}'
                                    and idLockerPortaCategoria = '{ms18.Categoria_Porta}'
                                    and idLockerPortaStatus = 1;"""
        record_Porta = conn.execute(command_sql).fetchone()
        if record_Porta is None:
            ms19['Codigo_Resposta_MS19'] = 'M06001 - Não existe porta disponível para esta categoria'
        else:
            ms19['ID_da_Porta_do_Locker'] = record_Porta[0]
            ms19['Codigo_Resposta_MS19'] = 'M06000 - Sucesso'


            command_sql = f"""SELECT `locker`.`idPais`,
                                            `locker`.`cep`,
                                            `locker`.`LockerCidade`,
                                            `locker`.`LockerBairro`,
                                            `locker`.`LockerEndereco`,
                                            `locker`.`LockerNumero`,
                                            `locker`.`LockerComplemento`,
                                            `locker`.`LockerLatLong`,
                                            `locker`.`idLockerCategoria`,
                                            `locker`.`idLockerOperacao`
                                    FROM `rede1minuto`.`locker`
                                    where locker.idLocker = '{ms18.ID_da_Estacao_do_Locker}';"""
            record = conn.execute(command_sql).fetchone()

            command_sql = f"""UPDATE `rede1minuto`.`locker_porta`
                                            SET `idLockerPortaStatus` = 2
                                        where locker_porta.idLockerPorta = '{record_Porta[0]}'
                                            AND idLockerPortaCategoria = '{ms0518.Categoria_Porta}';"""
            conn.execute(command_sql)

            ms19['Data_Hora_Resposta'] = dt_string
            ms19['Codigo_Pais_Locker'] = record[0]
            ms19['CEP_Locker'] = record[1]
            ms19['Cidade_Locker'] = record[2]
            ms19['Bairro_Locker'] = record[3]
            ms19['Endereco_Locker'] = record[4]
            ms19['Numero_Locker'] = record[5]
            ms19['LatLong'] = record[6]
            ms19['Categoria_Locker'] = record[7]
            ms19['Modelo_Operacao_Locker'] = record[8]
            ms19['Categoria_Porta'] = ms18.Categoria_Porta

            idTransacaoUnica = str(uuid.uuid1())
            insert_ms18(ms18, idTransacaoUnica)

            ms19['ID_Transacao_Unica'] = idTransacaoUnica
            ms19['ID_Geracao_QRCODE'] = idTransacaoUnica

            Codigo_Abertura_Porta = random.randint(100000000000, 1000000000000)
            ms19['Codigo_Abertura_Porta'] = Codigo_Abertura_Porta

            Inicio_reserva = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            date_after = datetime.now() + timedelta(days=3)  # 3 é o valor Default
            Final_reserva = date_after.strftime('%Y-%m-%d %H:%M:%S')

            ms19['DataHora_Inicio_Locacao'] = ms18.Inicio_reserva
            ms19['DataHora_Final_Locacao'] = ms18.Final_reserva

        return ms19
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms19'] = sys.exc_info()
        return result

###### Enviar para fila ############


def insert_ms18(ms18, idTransacaoUnica, record_Porta, Inicio_reserva):
    try:
        command_sql = f'''INSERT INTO `rede1minuto`.`reserva_locacao`
                                        (`IdTransacaoUnica`,
                                        `IdSolicitante`,
                                        `IdReferencia`,
                                        `idRede`,
                                        `idLocker`,
                                        `idLockerPorta`,
                                        `DataHoraSolicitacao`,
                                        `idStatusReserva`,
                                        `TipoFluxoAtual`)
                                    VALUES
                                        ('{idTransacaoUnica}',
                                        '{ms18.ID_do_Solicitante}',
                                        '{ms18.ID_de_Referencia}',
                                        {ms18.ID_Rede_Lockers},
                                        '{ms18.ID_da_Estacao_do_Locker}',
                                        '{record_Porta[0]}',
                                        '{Inicio_reserva}',
                                        {1}, 
                                        {0});''' # 1 - Reserva efetivada, 2 - Reserva cancelada, 3 - Reserva em andamento, 4 - Reserva em espera
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error insert_ms18'] = sys.exc_info()
        return result