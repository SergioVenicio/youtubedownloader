import os

import pika
from dotenv import load_dotenv

from youtube_downloader.settings import env_file


load_dotenv(env_file)


class Connection():
    def connect(self):
        credentials = pika.PlainCredentials(
            username=os.getenv('AMQ_USER', 'guest'),
            password=os.getenv('AMQ_PASSWORD', 'guest')
        )

        params = pika.ConnectionParameters(
            host=os.getenv('AMQ_HOST', 'localhost'),
            port=os.getenv('AMQ_CONNECTIONS_PORT', 15672),
            virtual_host=os.getenv('AMQ_VHOST', '/'),
            credentials=credentials
        )

        return pika.BlockingConnection(
            parameters=params
        )
