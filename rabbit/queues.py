import os
import aio_pika
import json
import time
import youtube_dl

from aio_pika.pool import Pool
from elasticsearch import Elasticsearch
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

OPTIONS = {
    'outtmpl': 'videos/%(title)s.%(ext)s',
}


class AsyncBaseQueue:
    def __init__(self, exchange, queue, key, io_loop):
        self.exchange = exchange
        self.queue = queue
        self.key = key
        self.io_loop = io_loop
        self.connection_pool = Pool(self.connect, max_size=5, loop=io_loop)
        self.channel_pool = Pool(self.get_channel, max_size=50, loop=io_loop)

    async def get_channel(self):
        async with self.connection_pool.acquire() as connection:
            return await connection.channel()

    async def connect(self):
        _user = os.getenv('AMQ_USER', 'guest')
        _pwd = os.getenv('AMQ_PASSWORD', 'guest')
        _host = os.getenv('AMQ_HOST', 'localhost')
        _port = os.getenv('AMQ_CONNECTIONS_PORT', 15672)
        _vhost = os.getenv('AMQ_VHOST', '/')
        conn = await aio_pika.connect_robust(
            f"amqp://{_user}:{_pwd}@{_host}:{_port}{_vhost}",
            loop=self.io_loop
        )

        return conn

    async def declare_exchange(self, channel):
        return await channel.declare_exchange(
            self.exchange, auto_delete=False
        )

    async def publish(self, body, content_type='text/plain'):
        if isinstance(body, dict):
            body = json.dumps(str(body))

        async with self.channel_pool.acquire() as channel:
            await channel.set_qos(10)
            exchange = await self.declare_exchange(channel)
            msg = await self.message(body, content_type)
            return await exchange.publish(msg, self.key)

    async def consume(self):
        await self.log(f"Consuming queue {self.queue}...")

        async with self.channel_pool.acquire() as channel:
            await channel.set_qos(10)
            queue = await channel.declare_queue(
                self.queue, auto_delete=False, durable=True, exclusive=False
            )
            await queue.bind(self.exchange, self.key)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    await self.callback(message)

    async def message(self, body, content_type='text/plain'):
        return aio_pika.Message(
            body.encode('utf-8'), content_type=content_type
        )

    async def log(self, msg):
        _time = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
        print(f"[{_time}] {msg}")

        els_msg = {
            'text': msg,
            'timestamp': _time
        }
        await Log(self.io_loop).publish(
            json.dumps(els_msg), content_type='application/json'
        )


class Log(AsyncBaseQueue):
    def __init__(self, io_loop, write=True):
        super().__init__('downloader', 'log_queue', 'log', io_loop)

        self.write = write
        self.es = Elasticsearch()
        self.time = 10

    async def callback(self, message):
        msg = json.loads(message.body.decode('utf8'))
        if self.write:
            try:
                self.es.index(
                    index='youtube_downloader',
                    id=msg['timestamp'],
                    body=msg
                )
            except Exception as e:
                print(e)
                time.sleep(self.time)
                self.time *= 2
            else:
                self.time = 10
                await message.ack()


class Videos(AsyncBaseQueue):
    def __init__(self, io_loop):
        super().__init__('downloader', 'videos_queue', 'videos', io_loop)

    async def callback(self, message):
        video = json.loads(message.body.decode('utf8'))
        await self.log(f"Downloading {video['url']}")
        with youtube_dl.YoutubeDL(OPTIONS) as ydl:
            try:
                ydl.extract_info(
                    video['url'], download=True
                )
            except Exception as e:
                await self.log(str(e))
                print(e)
            finally:
                await message.ack()

        return
