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
from fastapi import APIRouter, Depends, HTTPException
from config.db import conn
from config.log import logger
from auth.auth import AuthHandler
from schemas.ms03 import MS03
from schemas.ms04 import MS04, Locker, PortaLocker
from cryptography.fernet import Fernet
from config.log import logger
import pika
import sys
import os
import json

ms03_ms04 = APIRouter()
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

#@ms03_ms04.post("/ms03", tags=["ms04"], response_model=MS04, description="Consulta ao Catalogo de Estações Lockers")
@ms03_ms04.post("/msg/v01/lockers/slots", tags=["ms04"], description="Consulta ao Catalogo de Estações Lockers")
def ms03(ms03: MS03, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("Consulta ao Catalogo de Estações Lockers")
        logger.info(f"Usuário que fez a solicitação: {public_id}")
        if ms03.ID_do_Solicitante is None:
            raise HTTPException(status_code=422, detail="M02006 - ID_do_Solicitante obrigatório")
        if len(ms03.ID_do_Solicitante) != 20: # 20 caracteres
            raise HTTPException(status_code=422, detail="M04009 - ID_de_Solicitante inválido")
        if ms03.ID_Rede_Lockers is None:
            raise HTTPException(status_code=422, detail="M04007 - ID_Rede_Lockers obrigatório")
        if ms03.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms03.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M04010 - ID_Rede_Lockers inválido")
        if ms03.Data_Hora_Solicitacao is None:
            ms03.Data_Hora_Solicitacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if ms03.Codigo_Pais_Locker is None:
            ms03.Codigo_Pais_Locker = "BR" # Considerando Brasil com Default
        else:
            command_sql = f"SELECT idPais from Pais where Pais.idPais = '{ms03.Codigo_Pais_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M04012 - Codigo País_Locker inválido")
        if ms03.Cidade_Locker is not None:
            command_sql = f"SELECT cidade from cepbr_cidade where cidade = '{ms03.Cidade_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M04013 - Cidade_Locker inválido")
        if ms03.Cep_Locker is not None:
            command_sql = f"SELECT cep from cepbr_endereco where cepbr_endereco.cep = '{ms03.Cep_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M04014 - CEP_Locker inválido")
        if ms03.Bairro_Locker is not None:
            command_sql = f"SELECT bairro from cepbr_bairro where bairro = '{ms03.Bairro_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M04015 - Bairro_Locker inválido")
        if ms03.Endereco_Locker is not None:
            command_sql = f"SELECT logradouro from cepbr_endereco where cepbr_endereco.logradouro = '{ms03.Endereco_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M04016 - Endereco_Locker inválido")
        if ms03.Modelo_uso_Locker is not None:
            command_sql = f"SELECT idLockerPortaUso from locker_porta_uso where idLockerPortaUso = '{ms03.Modelo_uso_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M04019 - Modelo_uso_Locker inválido")    
        if ms03.Categoria_Locker is not None:
            command_sql = f"SELECT idLockerCategoria from locker_porta_categoria where idLockerCategoria = '{ms03.Categoria_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M04020 - Categoria_Locker inválido")    
        if ms03.Modelo_Operacao_Locker is not None:
            command_sql = f"SELECT locker_porta_operacao from locker_porta_operacao where idLockerOperacao = '{ms03.Modelo_Operacao_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M04021 - Modelo_Operacao_Locker inválido")    
        if ms03.Tipo_Armazenamento is not None:
            command_sql = f"SELECT `idLockerRefrigeracaoColuna` FROM `locker_refrigeracao_coluna` where idLockerRefrigeracaoColuna = {ms03.Tipo_Armazenamento};"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M04021 - Tipo_Armazenamento inválido")
        if ms03.ID_da_Estacao_do_Locker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{ms03.ID_da_Estacao_do_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M04022 - ID_da_Estacao_do_ Locker inválido")    
        if ms03.LatLong is not None:
            if not latlong_valid(ms03.LatLong):
                raise HTTPException(status_code=422, detail="M04023 - Latitude e Longitude inválido - (informe 'lat,long')")
        if ms03.Versao_Mensageria is not None:
            if ms03.Versao_Mensageria != "1.0.0":
                raise HTTPException(status_code=422, detail="M04025 - Versao_Mensageria inválido")    
        if ms03.Codigo_Dimensao_Portas_Locker is not None:
            command_sql = f"SELECT `idLockerPortaDimensao` FROM `locker_porta_dimensao` where idLockerPortaDimensao = '{ms03.Codigo_Dimensao_Portas_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                raise HTTPException(status_code=422, detail="M04028 - Codigo_Dimensao_Portas_Locker inválido")   

        command_sql = f"""INSERT INTO `MS03`
                            (`IdReferencia`,         
                            `IdSolicitante`,         
                            `idRede`,  
                            `DataHoraSolicitacao`,
                            `idPais`,
                            `cep`,
                            `LockerCidade`,
                            `LockerBairro`,
                            `LockerEndereco`,
                            `LockerNumero`,
                            `LockerComplemento`,
                            `idLockerUso`,
                            `idLockerCategoria`,
                            `idLockerRefrigeracaoColuna`,
                            `idLockerPortaDimensao`,
                            `idLockerOperacao`,
                            `idLocker`,
                            `LockerLatLong`,
                            `VersaoMensageria`)
                        VALUES
                            ('{ms03.ID_de_Referencia}',
                            '{ms03.ID_do_Solicitante}',
                            '{ms03.ID_Rede_Lockers}',
                            '{ms03.Data_Hora_Solicitacao}',
                            '{ms03.Codigo_Pais_Locker}',
                            '{ms03.Cep_Locker}',
                            '{ms03.Cidade_Locker}',
                            '{ms03.Bairro_Locker}',
                            '{ms03.Endereco_Locker}',
                            '{ms03.Numero_Locker}',
                            '{ms03.Complemento_Locker}',
                            {ms03.Modelo_uso_Locker},
                            {ms03.Categoria_Locker},
                            {ms03.Tipo_Armazenamento},
                            '{ms03.Codigo_Dimensao_Portas_Locker}',
                            {ms03.Modelo_Operacao_Locker},
                            '{ms03.ID_da_Estacao_do_Locker}',
                            '{ms03.LatLong}',
                            '{ms03.Versao_Mensageria}');"""    
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        conn.execute(command_sql)
        where = 0
        if ms03.ID_de_Referencia is None:
            ms03.ID_de_Referencia = "c67a298f-015f-4b65-a62b-8a6e42dc789a"
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
        ms04 = {}
        ms04['Codigo_de_MSG'] = "MS04"
        ms04['ID_de_Referencia'] = ms03.ID_de_Referencia
        ms04['ID_do_Solicitante'] = ms03.ID_do_Solicitante
        ms04['ID_Rede_Lockers'] = ms03.ID_Rede_Lockers
        ms04['Data_Hora_Resposta'] = dt_string

        command_sql = f"""
        SELECT `locker`.`idLocker`, `locker`.`idPais`, `locker`.`cep`,
                `locker`.`LockerCidade`, `locker`.`LockerBairro`,
                `locker`.`LockerEndereco`, `locker`.`LockerNumero`, `locker`.`LockerComplemento`,
                `locker`.`LockerNomeFantasia`, `locker_uso`.`LockerUsoDescricao`,
                `locker_categoria`.`LockerCategoriaDescricao`,
                `locker_refrigeracao_coluna`.`LockerRefrigeracaoColunaDescricao`,
                `locker_operacao`.`LockerOperacaoDescricao`,
                ST_ASTEXT(`locker`.`LockerLatLong`)
        FROM
            ((((`locker`
            JOIN `locker_uso` ON (`locker_uso`.`idLockerUso` = `locker`.`idLockerUso`))
            JOIN `locker_categoria` ON (`locker_categoria`.`idLockerCategoria` = `locker`.`idLockerCategoria`))
            JOIN `locker_refrigeracao_coluna` ON (`locker_refrigeracao_coluna`.`idLockerRefrigeracaoColuna` = `locker`.`idLockerRefrigeracaoColuna`))
            JOIN `locker_operacao` ON (`locker_operacao`.`idLockerOperacao` = `locker`.`idLockerOperacao`))
            where `idRede` = '{ms03.ID_Rede_Lockers}'"""
        if ms03.Codigo_Pais_Locker is not None:
            command_sql += f" and `idPais` = '{ms03.Codigo_Pais_Locker}'"
        if ms03.Cep_Locker is not None:
            command_sql += f" and `cep` = '{ms03.Cep_Locker}'"
        if ms03.Cidade_Locker is not None:
            command_sql += f" and `LockerCidade` = '{ms03.Cidade_Locker}'"
        if ms03.Bairro_Locker is not None:
            command_sql += f" and `LockerBairro` = '{ms03.Bairro_Locker}'"
        if ms03.Endereco_Locker is not None:
            command_sql += f" and LockerEndereco = '{ms03.Endereco_Locker}'"
        if ms03.Numero_Locker is not None:
            command_sql += f" and LockerNumero = '{ms03.Numero_Locker}'"
        if ms03.Modelo_uso_Locker is not None:
            command_sql += f" and `locker_uso`.`idLockerUso` = '{ms03.Modelo_Uso_Locker}'"
        if ms03.Categoria_Locker is not None:
            command_sql += f" and `locker_categoria`.`idLockerCategoria` = '{ms03.Categoria_Locker}'"
    #    if idLockerRefrigeracaoColuna is not None:
    #        command_sql += " and `locker_refrigeracao_coluna`.`idLockerRefrigeracaoColuna` = '{0}'".format(idLockerRefrigeracaoColuna)
        if ms03.Modelo_Operacao_Locker is not None:
            command_sql += f" and `locker_operacao`.`idLockerOperacao` = '{ms03.Modelo_Operacao_Locker}'"
        if ms03.Codigo_Dimensao_Portas_Locker is not None:
            command_sql += f" and `locker_porta_dimensao`.`idLockerPortaDimensao` = '{ms03.Codigo_Dimensao_Portas_Locker}'"
        if ms03.ID_da_Estacao_do_Locker is not None:
            command_sql += f" and `idLocker` = '{ms03.ID_da_Estacao_do_Locker}'"
        if ms03.LatLong is not None:
            command_sql += f" and `LockerLatLong` = '{ms03.Latlong}'"
        command_sql = command_sql.replace("'None'", "Null")
        command_sql = command_sql.replace("None", "Null")
        records = conn.execute(command_sql).fetchall()
        locker = {}
        lockers = []
        for row in records:
            locker['Id_da_Estacao_do_Locker'] = row[0]
            locker['Codigo_Pais_Locker'] = row[1]
            locker['CEP_Locker'] = row[2]
            locker['Cidade_Locker'] = row[3]
            locker['Bairro_Locker'] = row[4]
            locker['Endereco_Locker'] = row[5]
            locker['Numero_Locker'] = row[6]
            locker['Complemento_Locker'] = row[7]
            locker['Nome_Fantasia_do_Locker'] = row[8]
            locker['LockerUso'] = row[9]
            locker['Categoria_Locker'] = row[10]
            locker['Tipo_Armazenamento'] = row[11]
            locker['Modelo_Operacao_Locker'] = row[12]
            locker['LatLong'] = row[13]
            lockers.append(locker)
        for locker_porta in records:
            command_sql = f"""
            SELECT   `locker_porta`.`idLockerPorta`, `locker_porta`.`idLockerPortaFisica`,
                        `locker_porta_categoria`.`LockerPortaCategoriaDescricao`,
                        `locker_porta_uso`.`LockerPortaUsoDescricao`,
                        `locker_porta_operacao`.`LockerPortaOperacaoDescricao`,
                        `locker_porta_dimensao`.`LockerPortaDimensaoSigla`,
                        `locker_porta_dimensao`.`LockerportadimensaoDescricao`,
                        `locker_porta_dimensao`.`LockerPortaComprimento`,
                        `locker_porta_dimensao`.`LockerPortaLargura`,
                        `locker_porta_dimensao`.`LockerPortaAltura`,
                        `locker_porta_dimensao`.`LockerPortaPesoMax`
            FROM
                    ((((`locker_porta`
                    JOIN `locker_porta_categoria` ON (`locker_porta_categoria`.`idLockerPortaCategoria` = `locker_porta`.`idLockerPortaCategoria`))
                    JOIN `locker_porta_uso` ON (`locker_porta_uso`.`idLockerPortaUso` = `locker_porta`.`idLockerPortaUso`))
                    JOIN `locker_porta_operacao` ON (`locker_porta_operacao`. `idLockerPortaOperacao` = `locker_porta`.`idLockerPortaOperacao`))
                    JOIN `locker_porta_dimensao` ON (`locker_porta_dimensao`.`idLockerPortaDimensao` = `locker_porta`.`idLockerPortaDimensao`))
                    WHERE `locker_porta`.`idLockerPortaStatus` = 1
                        AND `locker_porta`.`idLocker` = '{locker_porta[0]}'"""
            command_sql = command_sql.replace("'None'", "Null")
            command_sql = command_sql.replace("None", "Null")
            records0 = conn.execute(command_sql).fetchall()
            portalocker = {}
            portas = []
            for row in records0:
                portalocker['ID_da_Porta_do_Locker'] = row[0]
                portalocker['idLockerPortaFisica'] = row[1]
                portalocker['Categoria_Porta'] = row[2]
                portalocker['Modelo_Uso_Porta'] = row[3]
                portalocker['LockerPortaOperacao'] = row[4]
                portalocker['Codigo_Dimensao_Portas_Locker'] = row[5]
                portalocker['Comprimento_Porta'] = row[6]
                portalocker['Largura_Porta'] = row[7]
                portalocker['Altura_Porta'] = row[8]
                portalocker['Peso_Maximo_Porta'] = row[9]
                portas.append(portalocker)
            for locker in lockers:
                if locker['Id_da_Estacao_do_Locker'] == locker_porta[0]:
                    locker['Portas'] = portas
        ms04['lockers'] = lockers
        ms04['Versao_Mensageria'] = ms03.Versao_Mensageria

        return ms04
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms03'] = sys.exc_info()
        return result