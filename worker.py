# External
from datetime import datetime
import youtube_dl

from rabbit import queues


OPTIONS = {
    'outtmpl': 'videos/%(title)s.%(ext)s',
}

# Video QUEUE
video_comsumer = queues.VideoQueue()
video_comsumer.setup_consumer()

# Logger Queue
logger_publisher = queues.LoggerQueue()
logger_publisher.setup_publisher()

# Error QUEUE
error_publisher = queues.ErrorQueue()
error_publisher.setup_publisher()


def callback(channel, method, properties, body):
    decoded_body = body.decode('utf-8')

    print(" [x] Received {%s}..." % decoded_body)

    try:
        with youtube_dl.YoutubeDL(OPTIONS) as ydl:
            response = ydl.extract_info(body.decode('utf-8'), download=True)
    except Exception as e:
        error = str(e)
        logger_publisher.publish_msg({
            'date': str(datetime.now()),
            'error': error,
            'service': 'video_consumer',
        })
        error_publisher.publish_msg(body)
    else:
        print(" [x] Result {%s}" % response['title'])

    channel.basic_ack(delivery_tag=method.delivery_tag)


video_comsumer.start_consuming(
    callback
)
