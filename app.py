import json
import asyncio
import uvloop

from sanic import response
from signal import signal, SIGINT

from main import app
from rabbit import queues
from sanic_cors import CORS


CORS(app)


@app.route('/')
async def index(request):
    return response.json({
        "status": "OK"
    })


@app.route('/download', methods=['POST', 'OPTIONS'])
async def download(request):
    async for url in get_urls(request.json.get('url')):
        await publish(url)
    return response.json({'stauts': 'OK'})


async def get_urls(urls):
    for url in set(urls.split(';')):
        yield url


async def publish(url):
    video_publisher = queues.Videos(asyncio.get_event_loop())
    msg = json.dumps({'url': url})
    await video_publisher.publish(msg, content_type='application/json')


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
