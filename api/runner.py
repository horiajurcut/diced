import asyncio

from aiohttp import web
from api.handlers import RoutesHandler
from api.routes import register_routes


async def init(loop):
    app = web.Application(loop=loop)
    handler = RoutesHandler()

    register_routes(app, handler)
    host, port = '0.0.0.0', 8080

    return app, host, port


def main():
    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init(loop))
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()
