# -*- coding: utf-8 -*-

from typing import Any
from sqlalchemy import create_engine
from json import dumps
import logging
import traceback
import json
import sys
import logging.config
import uuid  # for public id
import jwt
from datetime import datetime, timedelta
from functools import wraps
import ast
from fastapi import APIRouter, Depends, HTTPException
from config.db import conn
from config.log import logger
from auth.auth import AuthHandler
from schemas.ms01 import MS01
from schemas.ms02 import MS02, Locker
from cryptography.fernet import Fernet
import sys

ms01_ms02 = APIRouter()
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

#@ms01_ms02.post("/ms01", tags=["ms02"], response_model=MS04, description="Consulta ao Catalogo de Estações Lockers")
@ms01_ms02.post("/msg/v01/lockers", tags=["ms02"], description="Consulta ao Catalogo de Estações Lockers")
def ms01(ms01: MS01, public_id=Depends(auth_handler.auth_wrapper)):
    try:
        logger.info("Consulta ao Catalogo de Estações Lockers")
        logger.info(f"Usuário que fez a solicitação: {public_id}")
        if ms01.ID_do_Solicitante is None:
            return {"status_code":422, "detail":"M02006 - ID_do_Solicitante obrigatório"}
        if len(ms01.ID_do_Solicitante) != 20: # 20 caracteres
            return {"status_code":422, "detail":"M02009 - ID_de_Solicitante inválido"}
        if ms01.ID_Rede_Lockers is None:
            return {"status_code":422, "detail":"M02007 - ID_Rede_Lockers obrigatório"}
        if ms01.ID_Rede_Lockers is not None:
            command_sql = f"SELECT idRede from rede where rede.idRede = '{ms01.ID_Rede_Lockers}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code":422, "detail":"M02010 - ID_Rede_Lockers inválido"}             
        if ms01.Data_Hora_Solicitacao is None:
            ms01.Data_Hora_Solicitacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if ms01.Codigo_Pais_Locker is None:
            ms01.Codigo_Pais_Locker = "BR" # Considerando Brasil com Default
        else:
            command_sql = f"SELECT idPais from Pais where Pais.idPais = '{ms01.Codigo_Pais_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code":422, "detail":"M02012 - Codigo País_Locker inválido"}
        if ms01.Cidade_Locker is not None:
            command_sql = f"SELECT cidade from cepbr_cidade where cidade = '{ms01.Cidade_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code":422, "detail":"M02013 - Cidade_Locker inválido"}  # Cidade_Locker inválido
        if ms01.Cep_Locker is not None:
            command_sql = f"SELECT cep from cepbr_endereco where cepbr_endereco.cep = '{ms01.Cep_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code":422, "detail":"M02014 - CEP_Locker inválido"}
        if ms01.Bairro_Locker is not None:
            command_sql = f"SELECT bairro from cepbr_bairro where bairro = '{ms01.Bairro_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code":422, "detail":"M02015 - Bairro_Locker inválido"} 
        if ms01.Endereco_Locker is not None:
            command_sql = f"SELECT logradouro from cepbr_endereco where cepbr_endereco.logradouro = '{ms01.Endereco_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code":422, "detail":"M02016 - Endereco_Locker inválido"}
    #    if ms01.Modelo_uso_Locker is not None:
    #        command_sql = f"SELECT idLockerPortaUso from locker_porta_uso where idLockerPortaUso = '{ms01.Modelo_uso_Locker}';"
    #        if conn.execute(command_sql).fetchone() is None:
    #            raise HTTPException(status_code=422, detail="M02019 - Modelo_uso_Locker inválido")    
        if ms01.Categoria_Locker is not None:
            command_sql = f"SELECT idLockerCategoria from locker_categoria where idLockerCategoria = '{ms01.Categoria_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code":422, "detail":"M02020 - Categoria_Locker inválido"}
        if ms01.Modelo_Operacao_Locker is not None:
            command_sql = f"SELECT idLockerOperacao FROM locker_operacao where idLockerOperacao = '{ms01.Modelo_Operacao_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code":422, "detail":"M02021 - Modelo_Operacao_Locker inválido"}    
        if ms01.ID_da_Estacao_do_Locker is not None:
            command_sql = f"SELECT idLocker from locker where locker.idLocker = '{ms01.ID_da_Estacao_do_Locker}';"
            if conn.execute(command_sql).fetchone() is None:
                return {"status_code":422, "detail":"M02022 - ID_da_Estacao_do_ Locker inválido"}
        if ms01.LatLong is not None:
            if not latlong_valid(ms01.LatLong):
                return {"status_code":422, "detail":"M02023 - Latitude e Longitude inválido - (informe 'lat,long')"}
        if ms01.Versao_Mensageria is not None:
            if ms01.Versao_Mensageria != "1.0.0":
                return {"status_code":422, "detail":"M02025 - Versao_Mensageria inválido"}
        command_sql = f"""INSERT INTO `MS01`
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
                            ('{ms01.ID_de_Referencia}',
                            '{ms01.ID_do_Solicitante}',
                            '{ms01.ID_Rede_Lockers}',
                            '{ms01.Data_Hora_Solicitacao}',
                            '{ms01.Codigo_Pais_Locker}',
                            '{ms01.Cep_Locker}',
                            '{ms01.Cidade_Locker}',
                            '{ms01.Bairro_Locker}',
                            '{ms01.Endereco_Locker}',
                            '{ms01.Numero_Locker}',
                            '{ms01.Complemento_Locker}',
                            '{ms01.Modelo_Uso_Locker}',
                            '{ms01.Categoria_Locker}',
                            '{ms01.Tipo_Armazenamento}',
                            '{ms01.Codigo_Dimensao_Portas_Locker}',
                            '{ms01.Modelo_Operacao_Locker}',
                            '{ms01.ID_da_Estacao_do_Locker}',
                            '{ms01.LatLong}',
                            '{ms01.Versao_Mensageria}');"""
        command_sql = command_sql.replace("'None'", "Null")
        row = conn.execute(command_sql)
        where = 0
        if ms01.ID_de_Referencia is None:
            ms01.ID_de_Referencia = "Não informado"
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
        ms02 = dict()
        ms02['Codigo_de_MSG'] = ms01.Codigo_de_MSG
        ms02['ID_de_Referencia'] = ms01.ID_de_Referencia
        ms02['ID_do_Solicitante'] = ms01.ID_do_Solicitante
        ms02['ID_Rede_Lockers'] = ms01.ID_Rede_Lockers
        ms02['Versao_Mensageria'] = ms01.Versao_Mensageria
        ms02['Data_Hora_Resposta'] = dt_string

        command_sql = f"""select `locker`.`idPais`,
                                `locker`.`LockerCidade`,
                                `locker`.`cep`,
                                `locker`.`LockerBairro`,
                                `locker`.`LockerEndereco`,
                                `locker`.`LockerNumero`,
                                `locker`.`LockerComplemento`,
                                `locker_uso`.`LockerUsoDescricao`,
                                `locker_categoria`.`LockerCategoriaDescricao`,
                                `locker_refrigeracao_coluna`.`LockerRefrigeracaoColunaDescricao`,
                                `locker_operacao`.`LockerOperacaoDescricao`,
                                `locker`.`LockerNomeFantasia`,
                                `locker`.`idLocker`,
                                ST_ASTEXT(`locker`.`LockerLatLong`),
                                convert(`locker`.`SegundaHoraInicio`, char) SegundaHoraInicio, 
                                convert(`locker`.`SegundaHoraFim`, char) SegundaHoraFim, 
                                convert(`locker`.`TercaHoraInicio`, char) TercaHoraInicio,
                                convert(`locker`.`TercaHoraFim`, char) TercaHoraFim,
                                convert(`locker`.`QuartaHoraInicio`, char) QuartaHoraInicio, 
                                convert(`locker`.`QuartaHoraFim`, char) QuartaHoraFim,
                                convert(`locker`.`QuintaHoraInicio`, char) QuintaHoraInicio, 
                                convert(`locker`.`QuintaHoraFim`, char) QuintaHoraFim,
                                convert(`locker`.`SextaHoraInicio`, char) SextaHoraInicio,
                                convert(`locker`.`SextaHoraFim`, char) SextaHoraFim,
                                convert(`locker`.`SabadoHoraInicio`, char) SabadoHoraInicio,
                                convert(`locker`.`SabadoHoraFim`, char) SabadoHoraFim,
                                convert(`locker`.`DomingoHoraInicio`, char) DomingoHoraInicio, 
                                convert(`locker`.`DomingoHoraFim`, char) DomingoHoraFim,
                                convert(`locker`.`FeriadosHoraInicio`, char) FeriadosHoraInicio,
                                convert(`locker`.`FeriadosHoraFim`, char) FeriadosHoraFim
                    FROM
                        `locker`
                            JOIN `locker_uso` ON (`locker_uso`.`idLockerUso` = `locker`.`idLockerUso`)
                            JOIN `locker_categoria` ON (`locker_categoria`.`idLockerCategoria` = `locker`.`idLockerCategoria`)
                            JOIN `locker_refrigeracao_coluna` ON (`locker_refrigeracao_coluna`.`idLockerRefrigeracaoColuna` = `locker`.`idLockerRefrigeracaoColuna`)
                            JOIN `locker_operacao` ON (`locker_operacao`.`idLockerOperacao` = `locker`.`idLockerOperacao`)
                            where `locker`.`idRede` = {ms01.ID_Rede_Lockers}"""

        if ms01.Codigo_Pais_Locker is not None:
            command_sql += f" and `idPais` = '{ms01.Codigo_Pais_Locker}'"
        if ms01.Cep_Locker is not None:
            command_sql += f" and `cep` = '{ms01.Cep_Locker}'"
        if ms01.Cidade_Locker is not None:
            command_sql += f" and `LockerCidade` = '{ms01.Cidade_Locker}'"
        if ms01.Bairro_Locker is not None:
            command_sql += f" and `LockerBairro` = '{ms01.Bairro_Locker}'"
        if ms01.Endereco_Locker is not None:
            command_sql += f" and LockerEndereco = '{ms01.Endereco_Locker}'"
        if ms01.Numero_Locker is not None:
            command_sql += f" and LockerNumero = '{ms01.Numero_Locker}'"
        if ms01.Modelo_Uso_Locker is not None:
            command_sql += f" and `locker_uso`.`idLockerUso` = '{ms01.Modelo_Uso_Locker}'"
        if ms01.Modelo_Operacao_Locker is not None:
            command_sql += f" and `locker_operacao`.`idLockerOperacao` = '{ms01.Modelo_Operacao_Locker}'"
        if ms01.ID_da_Estacao_do_Locker is not None:
            command_sql += f" and `idLocker` = '{ms01.ID_da_Estacao_do_Locker}'"
        records = conn.execute(command_sql).fetchall()
        Locker = {}
        Estacao_Locker = []    
        for record in records:
            Locker['Codigo_Pais_Locker'] = record[0]
            Locker['Cidade_Locker'] = record[1]
            Locker['Cep_Locker'] = record[2]
            Locker['Bairro_Locker'] = record[3]
            Locker['Endereco_Locker'] = record[4]
            Locker['Numero_Locker'] = record[5]
            Locker['Complemento_Locker'] = record[6]
            Locker['Modelo_Uso_Locker'] = record[7]
            Locker['Categoria_Locker'] = record[8]
            Locker['Tipo_Armazenamento'] = record[9]
            Locker['Modelo_Operacao_Locker'] = record[10]
            Locker['Nome_Fantasia_do_locker'] = record[11]
            Locker['ID_da_estacao_do_locker'] = record[12]
            Locker['LatLong'] = record[13]
            Locker['Segunda_Hora_Inicio'] = record[14]
            Locker['Segunda_Hora_Fim'] = record[15]
            Locker['Terca_Hora_Inicio'] = record[16]
            Locker['Terca_Hora_Fim'] = record[17]
            Locker['Quarta_Hora_Inicio'] = record[18]
            Locker['Quarta_Hora_Fim'] = record[19]
            Locker['Quinta_Hora_Inicio'] = record[20]
            Locker['Quinta_Hora_Fim'] = record[21]
            Locker['Sexta_Hora_Inicio'] = record[22]
            Locker['Sexta_Hora_Fim'] = record[23]
            Locker['Sabado_Hora_Inicio'] = record[24]
            Locker['Sabado_Hora_Fim'] = record[25]
            Locker['Domingo_Hora_Inicio'] = record[26]
            Locker['Domingo_Hora_Fim'] = record[27]
            Locker['Feriados_Hora_Inicio'] = record[28]
            Locker['Feriados_Hora_Fim'] = record[29]
            Estacao_Locker.append(Locker)
        ms02['Estacao_Locker:'] = Estacao_Locker  
        return ms02
    except:
        logger.error(sys.exc_info())
        result = dict()
        result['Error ms01'] = sys.exc_info()
        return result
