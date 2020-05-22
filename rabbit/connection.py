import os

import aio_pika
import pika


class Connection():
    def connect(self):
        credentials = pika.PlainCredentials(
            username=os.environ.get('AMQ_USER', 'rabbitmq_user'),
            password=os.environ.get('AMQ_PASSWORD', 'rabbitmq_password')
        )

        params = pika.ConnectionParameters(
            host=os.environ.get('AMQ_HOST', 'localhost'),
            port=os.environ.get('AMQ_CONNECTIONS_PORT', 5672),
            virtual_host=os.environ.get('AMQ_VHOST', '/'),
            credentials=credentials
        )

        return pika.BlockingConnection(
            parameters=params
        )

    async def aio_connect(self, ioloop):
        host = os.environ.get('AMQ_HOST', 'localhost')
        port = os.environ.get('AMQ_CONNECTIONS_PORT', 5672)
        vhost = os.environ.get('AMQ_VHOST', '/')
        user = os.environ.get('AMQ_USER', 'rabbitmq_user')
        pwd = os.environ.get('AMQ_PASSWORD', 'rabbitmq_password')

        connection = await aio_pika.connect_robust(
            f"amqp://{user}:{pwd}@{host}:{port}{vhost}",
            loop=ioloop
        )

        return connection
