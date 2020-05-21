import os
import aio_pika
import asyncio
import json
import youtube_dl
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

    async def message(self, body):
        return aio_pika.Message(body, content_type='text/plain')


class AsyncVideos(AsyncBaseQueue):
    def __init__(self, io_loop):
        super().__init__('downloader', 'videos', 'videos_queue', io_loop)

    async def publish(self, body):
        if isinstance(body, dict):
            body = json.dumps(body)

        conn = await self.connect()
        channel = await conn.channel()
        exchange = await self.declare_exchange(channel)
        await exchange.publish(self.message(body), self.key)

        return

    async def callback(self, message):
        print(f'[*] consuming {self.queue} queue...')

        with youtube_dl.YoutubeDL(OPTIONS) as ydl:
            try:
                ydl.extract_info(
                    message.body.decode('utf-8'), download=True
                )
                await message.ack()
            except Exception as e:
                print(e)

    
    async def consume(self):
        conn = await self.connect()
        channel = await conn.channel()
        exchange = await self.declare_exchange(channel)
        queue = await channel.declare_queue(
            self.queue, auto_delete=False, durable=True
        )

        await queue.bind(exchange, self.key)
        await queue.consume(self.callback)

        return conn