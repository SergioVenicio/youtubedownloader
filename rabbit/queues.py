import json

from .connection import Connection


class BasicQueue():
    def __init__(self, exchange, queue, key):
        __conn = Connection()

        self.exchange = exchange
        self.queue = queue
        self.key = key

        # Connection with broker
        self.__open_conn = __conn.connect()

        # Create channels
        self.publisher_channel = self.__open_conn.channel()
        self.consumer_channel = self.__open_conn.channel()

    def queue_declare(self, durable=True):
        self.publisher_channel.queue_declare(
            queue=self.queue,
            durable=durable
        )

    def exchange_declare(self):
        self.publisher_channel.exchange_declare(
            exchange=self.exchange
        )

    def queue_bind(self):
        self.publisher_channel.queue_bind(
            exchange=self.exchange,
            queue=self.queue,
            routing_key=self.key
        )

    def publish_msg(self, body):
        if isinstance(body, dict):
            body = json.dumps(body)

        self.publisher_channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.key,
            body=body
        )

    def start_consuming(self, callback, auto_ack=False):
        self.consumer_channel.basic_consume(
            queue=self.queue,
            on_message_callback=callback,
            auto_ack=auto_ack
        )

        print(' [*] Start consuming from queue {%s}...' % self.queue)
        self.consumer_channel.start_consuming()

    def setup_publisher(self):
        self.exchange_declare()
        self.queue_declare()
        self.queue_bind()

    def setup_consumer(self):
        self.exchange_declare()
        self.queue_declare()


class AsyncBaseClass:
    def __init__(self, exchange, queue, key, loop):
        __conn = Connection()

        self.exchange = exchange
        self.queue = queue
        self.key = key

        # Connection 
        self.__open_conn = __conn.aio_connect(loop)


    async def queue_declare(self, durable=True):
        self.publisher_channel = await self.__open_conn.channel()

        queue = await self.publisher_channel.queue_declare(
            queue=self.queue,
            auto_delete=durable
        )
        self._queue = queue

    async def start_consuming(self, callback, auto_ack=False):
        print(' [*] Start consuming from queue {%s}...' % self.queue)
        await self._queue.consume(callback)


class VideoQueue(BasicQueue):
    def __init__(self):
        super().__init__('downloader', 'videos', 'videos_queue')


class LoggerQueue(BasicQueue):
    def __init__(self):
        super().__init__('downloader', 'logger', 'loger_queue')


class ErrorQueue(BasicQueue):
    def __init__(self):
        super().__init__('downloader', 'error', 'error_queue')
