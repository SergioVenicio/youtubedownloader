import asyncio
import uvloop

from sanic import response
from sanic.log import logger
from signal import signal, SIGINT

from main import app, template
from rabbit import queues


@app.route('/')
async def index(request):
    html_string = await template('home.html')
    return response.html(html_string)


@app.route('/download', methods=['POST'])
async def download(request):
    urls = request.form.get('url').split(';')
    list(map(publish, request.form.get('url').split(';')))
    return response.redirect('/')


def publish(msg):
    video_publisher = queues.VideoQueue()
    video_publisher.exchange_declare()
    video_publisher.queue_declare()
    video_publisher.queue_bind()

    video_publisher.publish_msg(msg)


if __name__ == '__main__':
    asyncio.set_event_loop(uvloop.new_event_loop())
    server_corotine = app.create_server(return_asyncio_server=True)
    loop = asyncio.get_event_loop()
    server_task = asyncio.ensure_future(server_corotine, loop=loop)
    signal(SIGINT, lambda s, f: loop.stop())
    server = loop.run_until_complete(server_task)
    server.after_start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    finally:
        server.before_stop()

        close_task = server.close()
        loop.run_until_complete(close_task)

        for connection in server.connections:
            connection.close_if_idle()

        server.after_stop()
