import sys
import asyncio

from rabbit import queues


__WORKERS__ = {
    'video': queues.Videos,
    'logger': queues.Log,
}


def get_workers(worker, loop):
    worker = __WORKERS__.get(worker)
    return worker(loop)


if __name__ == '__main__':
    print('Wating messages...')

    worker_name = 'video'
    try:
        worker_name = sys.argv[1]
    except IndexError:
        pass

    loop = asyncio.get_event_loop()
    worker = get_workers(worker_name, loop)
    conn = loop.run_until_complete(worker.consume())

    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(conn.close())
