import os
import asyncio
import aio_pika

from rabbit import async_queues


loop = asyncio.get_event_loop()
videos_queue = async_queues.AsyncVideos(loop)
conn = loop.run_until_complete(videos_queue.consume())

print('Wating messages...')

if __name__ == '__main__':
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(conn.close())