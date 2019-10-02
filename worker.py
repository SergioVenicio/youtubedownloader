import pika
import youtube_dl

RABBIT_USER='rabbitmq_user'
RABBIT_PWD='rabbitmq_password'
RABBIT_PORT='5672'

RABBIT_URL = f'amqp://{RABBIT_USER}:{RABBIT_PWD}@localhost:{RABBIT_PORT}/'

VIDEOS_QUEUE = 'videos'

OPTIONS = {
    'outtmpl': 'videos/%(title)s.%(ext)s',
}


def __connection_rabbit():
    new_conn = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
    new_conn.channel().queue_declare(queue=VIDEOS_QUEUE, durable=True)
    return new_conn


CHANNEL = __connection_rabbit().channel()


def callback(channel, method, properties, body):
    print(f" [x] Received {body.decode('utf-8')}")

    with youtube_dl.YoutubeDL(OPTIONS) as ydl:
        response = ydl.extract_info(body.decode('utf-8'), download=True)

    print(f" [x] Result {response['title']}")


CHANNEL.basic_consume(
    queue=VIDEOS_QUEUE, auto_ack=True, on_message_callback=callback
)

CHANNEL.start_consuming()
