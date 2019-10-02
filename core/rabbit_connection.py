import pika
from youtube_downloader.settings import RABBIT_URL, VIDEOS_QUEUE


def __connection_rabbit():
    new_conn = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
    new_conn.channel().queue_declare(queue=VIDEOS_QUEUE, durable=True)
    return new_conn


CHANNEL = __connection_rabbit().channel()


def insert_in_queue(url):
    CHANNEL.basic_publish(exchange='', routing_key=VIDEOS_QUEUE, body=url)
