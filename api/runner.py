import asyncio

from aiohttp import web
from aiocassandra import aiosession
from api.handlers import RoutesHandler
from api.routes import register_routes
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

KEYSPACE = "diced"


async def init(loop):
    # Connect to Cassandra cluster
    cluster = Cluster(
        ["cassandra"],
        load_balancing_policy=DCAwareRoundRobinPolicy(),
        port=9042)
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)
    aiosession(session)

    app = web.Application(loop=loop)
    handler = RoutesHandler(session)

    register_routes(app, handler)
    host, port = "0.0.0.0", 8080

    return app, host, port


def main():
    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init(loop))
    web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    main()
