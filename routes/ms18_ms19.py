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
import pika

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


@ms18_ms19.post("/msg/v01/lockers/slot/rent", tags=["ms18"], description="Solicitação de Locação de Porta em Locker")
def ms18(ms18: MS18, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("MS18 - Solicitação de Locação de Porta em Locker")
        logger.info(ms18)
        logger.info(public_id)

        # validando ID_do_Solicitante
        if ms18.ID_do_Solicitante is None:
            return {"status_code": 422, "detail": "M019001 - ID_do_Solicitante obrigatório"}
        if len(ms18.ID_do_Solicitante) != 20: # 20 caracteres
            return {"status_code": 422, "detail": "M019002 - ID_do_Solicitante deve conter 20 caracteres"}

        # validando ID_Rede_Lockers
        if ms18.ID_Rede_Lockers is None:
            return {"status_code": 422, "detail": "M019003 - ID_Rede_Lockers obrigatório"}
        if ms18.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms18.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M019004 - ID_Rede_Lockers inválido"}

        # gerando Data_Hora_Solicitacao
        if ms18.Data_Hora_Solicitacao is None:
            now = datetime.now() - timedelta(hours=3)
            dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
            ms18.Data_Hora_Solicitacao = dt_string

        # validando ID_da_Estacao_do_Locker
        if ms18.ID_da_Estacao_do_Locker is None:
            return {"status_code": 422, "detail": "M019005 - ID_da_Estacao_do_Locker obrigatório"}
        if ms18.ID_da_Estacao_do_Locker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{ms18.ID_da_Estacao_do_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M019006 - ID_da_Estacao_do_ Locker inválido"}

        # validando Categoria_Porta
        if ms18.Categoria_Porta is None:
            return {"status_code": 422, "detail": "M019007 - Categoria_Porta obrigatório"}
        if ms18.Categoria_Porta is not None:
            command_sql = f"SELECT idLockerPortaCategoria from locker_porta_categoria where locker_porta_categoria.idLockerPortaCategoria = '{ms18.Categoria_Porta}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code": 422, "detail": "M019008 - Categoria_Porta inválido"}

        # validando versao mensageria
        if ms18.Versao_Mensageria is None:
            ms18.Versao_Mensageria = "1.0.0"

        # validando DataHora_Inicio_Locacao
        if ms18.DataHora_Inicio_Locacao is None:
            return {"status_code": 422, "detail": "M019007 - DataHora_Inicio_Locacao obrigatório"}

        # validando DataHora_Final_Locacao
        if ms18.DataHora_Final_Locacao is None:
            return {"status_code": 422, "detail": "M019007 - DataHora_Final_Locacao obrigatório"}

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
        idTransacaoUnica = str(uuid.uuid1())

        ms19 = {}
        ms19['Codigo_de_MSG'] = "MS19"
        ms19['ID_de_Referencia'] = ms18.ID_de_Referencia
        ms19['ID_do_Solicitante'] = ms18.ID_do_Solicitante
        ms19['ID_Rede_Lockers'] = ms18.ID_Rede_Lockers
        ms19['ID_da_Estacao_do_Locker'] = ms18.ID_da_Estacao_do_Locker

        command_sql = f"""SELECT idLockerPorta,
                                    idLockerPortaFisica
                                    FROM `rede1minuto`.`locker_porta`
                                    where locker_porta.idLocker = '{ms18.ID_da_Estacao_do_Locker}'
                                    and idLockerPortaCategoria = '{ms18.Categoria_Porta}'
                                    and idLockerPortaStatus = 1;"""
        record_Porta = conn.execute(command_sql).fetchone()
        if record_Porta is None:
            ms19['Codigo_Resposta_MS19'] = 'M019009 - Não existe porta disponível para esta categoria'
        else:
            ms19['ID_da_Porta_do_Locker'] = record_Porta[0]
            ms19['Codigo_Resposta_MS19'] = 'M019000 - Sucesso'


            command_sql = f"""SELECT `locker`.`idPais`,
                                            `locker`.`cep`,
                                            `locker`.`LockerCidade`,
                                            `locker`.`LockerBairro`,
                                            `locker`.`LockerEndereco`,
                                            `locker`.`LockerNumero`,
                                            `locker`.`LockerComplemento`,
                                            ST_ASTEXT(`locker`.`LockerLatLong`)LockerLatLong,
                                            `locker`.`idLockerCategoria`,
                                            `locker`.`idLockerOperacao`
                                    FROM `rede1minuto`.`locker`
                                    where locker.idLocker = '{ms18.ID_da_Estacao_do_Locker}';"""
            record = conn.execute(command_sql).fetchone()

            command_sql = f"""UPDATE `rede1minuto`.`locker_porta`
                                            SET `idLockerPortaStatus` = 2
                                        where locker_porta.idLockerPorta = '{record_Porta[0]}'
                                            AND idLockerPortaCategoria = '{ms18.Categoria_Porta}';"""
            conn.execute(command_sql)

            ms19['Data_Hora_Resposta'] = dt_string
            ms19['Codigo_Pais_Locker'] = record[0]
            ms19['CEP_Locker'] = record[1]
            ms19['Cidade_Locker'] = record[2]
            ms19['Bairro_Locker'] = record[3]
            ms19['Endereco_Locker'] = record[4]
            ms19['Numero_Locker'] = record[5]
            ms19['LockerComplemento'] = record[6]
            ms19['LatLong'] = record[7]
            ms19['Categoria_Locker'] = record[8]
            ms19['Modelo_Operacao_Locker'] = record[9]
            ms19['Categoria_Porta'] = ms18.Categoria_Porta
            ms19['ID_Transacao_Unica'] = idTransacaoUnica
#            ms19['ID_Geracao_QRCODE'] = idTransacaoUnica - Determinção do cliente passa a ser o codigo de abertura da porta

            Codigo_Abertura_Porta = str(random.randint(100000000000, 1000000000000))
            ms19['Codigo_Abertura_Porta'] = Codigo_Abertura_Porta
            ms19['ID_Geracao_QRCODE'] = Codigo_Abertura_Porta

            ms19['DataHora_Inicio_Locacao'] = ms18.DataHora_Inicio_Locacao
            ms19['DataHora_Final_Locacao'] = ms18.DataHora_Final_Locacao

        insert_locacao(ms18,idTransacaoUnica)
        insert_tracking_porta(ms18)
        insert_tracking_locacao(ms18, idTransacaoUnica)
        #send_lc01_mq(ms18, idTransacaoUnica, record_Porta)

        return ms19
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms18'] = sys.exc_info()
        return {"status_code": 500, "detail": "MS18 - Solicitação de Locação de Porta em Locker"}

###### Enviar para fila ############

def insert_locacao(ms18, idTransacaoUnica):
    try:
        command_sql = f"""SELECT idLockerPorta
                                    FROM `rede1minuto`.`locker_porta`
                                    where locker_porta.idLocker = '{ms18.ID_da_Estacao_do_Locker}'
                                    and idLockerPortaCategoria = '{ms18.Categoria_Porta}';"""
        record_Porta = conn.execute(command_sql).fetchone()
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
                                                            NOW(),
                                                            {1}, 
                                                            {0});'''  # 1 - Reserva efetivada, 2 - Reserva cancelada, 3 - Reserva em andamento, 4 - Reserva em espera
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error insert_locacao'] = sys.exc_info()
        return result

def insert_tracking_locacao(ms18, idTransacaoUnica):
    try:
        idTicketOcorrencia = str(uuid.uuid1())
        command_sql = f'''INSERT INTO `rede1minuto`.`tracking_locacao`
                                        (`idTicketOcorrencia`,
                                        `IdTransacaoUnica`,
                                        `idRede`,
                                        `idOcorrencia`,
                                        `DataHoraOcorrencia`,
                                        `idStatusLocacaoAnterior`,
                                        `idStatusLocacaoAtual`,
                                        `TipoFluxoAnterior`,
                                        `TipoFluxoAtual`)
                                    VALUES
                                        ('{idTicketOcorrencia}',
                                        '{idTransacaoUnica}',
                                        {ms18.ID_Rede_Lockers},
                                        null,
                                        NOW(),
                                        {0},
                                        {1},
                                        {0},
                                        {0});'''  # 1 - Reserva efetivada, 2 - Reserva cancelada, 3 - Reserva em andamento, 4 - Reserva em espera
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error insert_tracking'] = sys.exc_info()
        return result


def insert_tracking_porta(ms18):
    try:
        command_sql = f"""SELECT idLockerPorta
                                                    FROM `rede1minuto`.`locker_porta`
                                                    where locker_porta.idLocker = '{ms18.ID_da_Estacao_do_Locker}'
                                                    and idLockerPortaCategoria = '{ms18.Categoria_Porta}';"""
        record_Porta = conn.execute(command_sql).fetchone()
        idTicketOcorrencia = str(uuid.uuid1())
        command_sql = f'''INSERT INTO `rede1minuto`.`tracking_portas`
                                        (`idTicketOcorrencia`,
                                        `idRede`,
                                        `idLocker`,
                                        `idLockerPorta`,
                                        `idOcorrencia`,
                                        `DataHoraOcorrencia`,
                                        `idStatusPortaAnterior`,
                                        `idStatusPortaAtual`,
                                        `TipoFluxoAnterior`,
                                        `TipoFluxoAtual`)
                                    VALUES
                                        ('{idTicketOcorrencia}',
                                        {ms18.ID_Rede_Lockers},
                                        '{ms18.ID_da_Estacao_do_Locker}',
                                        '{record_Porta[0]}',
                                        null,
                                        NOW(),
                                        {0},
                                        {2},
                                        {0},
                                        {0});'''  # 1 - Reserva efetivada, 2 - Reserva cancelada, 3 - Reserva em andamento, 4 - Reserva em espera
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        logger.warning(command_sql)
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error insert_tracking_porta'] = sys.exc_info()
        return result





def send_lc01_mq(ms18, idTransacaoUnica, record_Porta):
    try:  # Envia LC01 para fila do RabbitMQ o aplicativo do locker a pega lá

        lc01 = {}
        lc01["CD_MSG"] = "LC01"

        content = {}
        content["ID_Referencia"] = ms18.ID_de_Referencia
        content["ID_Solicitante"] = ms18.ID_do_Solicitante
        content["ID_Rede"] = ms18.ID_Rede_Lockers
        content["ID_Transacao"] = idTransacaoUnica
        content["idLocker"] = ms18.ID_da_Estacao_do_Locker
        content["idLockerPorta"] = record_Porta[0]
        content["idLockerPortaFisica"] = record_Porta[1]
        content["DT_InicioReservaLocacao"] = ms18.DataHora_Inicio_Locacao
        content["DT_finalReservaLocacao"] = ms18.DataHora_Final_Locacao
        content["Versão_Software"] = "0.1"
        content["Versao_Mensageria"] = "1.0.0"

        lc01["Content"] = content

        MQ_Name = 'Rede1Min_MQ'
        URL = 'amqp://rede1min:Minuto@167.71.26.87' # URL do RabbitMQ
        queue_name = ms18.ID_da_Estacao_do_Locker + '_locker_output' # Nome da fila do RabbitMQ

        url = os.environ.get(MQ_Name, URL)
        params = pika.URLParameters(url)
        params.socket_timeout = 6

        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        message = json.dumps(lc01) # Converte o dicionario em string

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
        result['Error send_lc01_mq'] = sys.exc_info()
        return result
