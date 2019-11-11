import os

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
