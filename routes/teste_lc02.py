import requests
import logging
import json
import sys

try:
#    url = "http://137.184.137.84:80/login"
#    url = "http://127.0.0.1:8000/login"
    url = "http://ec2-34-206-134-100.compute-1.amazonaws.com:8008/login"
    payload = {
    "username": "Pico",
    "email": "pico.mirandola@gmail.com",
    "password": "23-11-DellaM"
    }
    print("----B")
    response = requests.request("POST", url, json=payload)
    token_dict = json.loads(response.content)
    token = "Bearer " + token_dict['token']
    headers = {'Authorization': token}
    print(token)
    ms11 = {"Codigo_de_MSG": "MS11",
            "ID_de_Referencia": "517452990001",
            "ID_do_Solicitante": "51745299000144001001",
            "ID_Rede_Lockers": 1,
            "ID_Transacao_Unica": "79fac49d-7f45-41a5-a1af-2cf36aeec46b",
            "ID_do_Remetente_Notificacao": "string",
            "ID_do_Destinatario_Notificacao": "string",
            "Tipo_de_Servico_Reserva": 2,
            "Status_Reserva_Anterior": 1,
            "Status_Reserva_Atual": 4,
            "Data_Hora_Notificacao_Evento_Reserva": "2021-11-11T20:20:27",
            "Versao_Mensageria": "1.0.0"}
    url = "http://137.184.137.84:80/msg/v01/lockers/order/tracking"
#    url = "http://127.0.0.1:8000/msg/v01/lockers"
#    url = "http://ec2-34-206-134-100.compute-1.amazonaws.com:8008/msg/v01/lockers"
    print(headers)
    response = requests.request("POST", url, json=ms11, headers=headers)
    print(response.content)
    parsed = json.loads(response.content)
    pretty = json.dumps(parsed, indent=4, sort_keys=True)
    print(pretty)
except Exception as e:
    logging.critical(e, exc_info=True)