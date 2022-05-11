import pika
import ssl

from config.log import logger
from config.config import ConfigServer

config = ConfigServer()

class RabbitMQ:
    def __init__(self):
        try:
            self.rabbitmq_config = config.get_rabbitmq_config()

            user = self.rabbitmq_config["USER"]
            password = self.rabbitmq_config["PASSWORD"]
            region = self.rabbitmq_config["REGION_AWS"]
            rabbitmq_broker_id = self.rabbitmq_config["BROKER_ID_AWS"]
            port = self.rabbitmq_config["PORT"]

            # SSL Context for TLS configuration of Amazon MQ for RabbitMQ
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')

            url = f"amqps://{user}:{password}@{rabbitmq_broker_id}.mq.{region}.amazonaws.com:{port}"
            self.parameters = pika.URLParameters(url)
            self.parameters.ssl_options = pika.SSLOptions(context=ssl_context)

            
        except Exception as e:
            logger.error(e)


        
    def send_locker_queue(self,idLocker, message):
        try:
            print("Enviando mensagem ao locker: " + idLocker)
            name_queue = idLocker + '_locker_output'
            name_exchange = 'amq.direct'
            connection = pika.BlockingConnection(self.parameters)
            channel = connection.channel()
            
            channel.queue_declare(queue=name_queue,durable=True)

            channel.queue_bind(exchange=name_exchange,
                   queue=name_queue)

            channel.basic_publish(
            exchange=name_exchange,
            routing_key=name_queue,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
    
            connection.close

        except pika.exceptions.AMQPChannelError as err:
            message_info = "Caught a channel error: {}, stopping...".format(err)
            logger.error(message_info)
            
        except pika.exceptions.AMQPConnectionError as err_connection:
            message_info = "A conexão foi perdida. {}, Tentando reconectar...".format(err_connection)
            logger.error(message_info)
            
