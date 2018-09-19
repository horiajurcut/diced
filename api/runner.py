import asyncio
import pathlib

from aiohttp import web
from aiocassandra import aiosession
from api.db_store import DbStore
from api.handlers import RoutesHandler
from api.routes import register_routes
from api.utils import load_config
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

PROJECT_ROOT = pathlib.Path(__file__).parent.parent


async def init(loop):
    # Load configuration file
    config = load_config(PROJECT_ROOT / 'config' / 'config.yml')

    # Connect to Cassandra cluster
    cluster = Cluster(
        [config["cassandra"]["host"]],
        load_balancing_policy=DCAwareRoundRobinPolicy(),
        port=config["cassandra"]["port"])
    session = cluster.connect()

    # Set keyspace
    session.set_keyspace(config["cassandra"]["keyspace"])

    # Threaded Cassandra wrapper for asyncio
    aiosession(session)

    # Setup database store
    db_store = DbStore(session, config)

    # Setup server application
    app = web.Application(loop=loop)
    handler = RoutesHandler(db_store, config)
    register_routes(app, handler)
    host, port = config["api"]["host"], config["api"]["port"]

    return app, host, port


def main():
    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init(loop))
    web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    main()
