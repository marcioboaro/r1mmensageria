import pika
import sys
import os
import json


class ConfigServer:

    def __init__(self):
        # Lê o arquivo de configurações
        config_file = open('config/config.json')
        self.config_data = json.load(config_file)
        self.enviroment = self.config_data["ENVIROMENT"]
        #print(self.config_data)

    def get_database_config(self) -> None:
        database_config = self.config_data["DATABASE"][self.enviroment]
        print("Database: " + str(database_config))
        return database_config


    def get_rabbitmq_config(self) -> None:
        rabbit_config = self.config_data["RABBITMQ"][self.enviroment]
        print("RabbitMQ: " + str(rabbit_config))
        return rabbit_config

    def get_users_notification_config(self) -> None:
        users_notification_config = self.config_data["USERS_NOTIFICATION"]
        print("Users Notification: " + str(users_notification_config))
        return users_notification_config

   
