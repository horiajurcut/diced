import random
import trafaret

from aiohttp import web
from api.utils import encode as base62_encode
from api.counter import get_increment
from cassandra import ConsistencyLevel
from cassandra.query import BatchStatement
from cassandra.query import SimpleStatement


class RoutesHandler:

    def __init__(self, session, config):
        self.session = session
        self.config = config

    async def index(self, request):
        return web.json_response({
            "message": "dice.it - The Fancy URL Shortener"
        })

    async def redirect(self, request):
        short_url = request.match_info["short_url"]

        query = """
            SELECT long_url FROM short_long WHERE short_url = '%s' LIMIT 1
        """ % short_url

        # We explicitly do not set a consistency level for high availability
        rows = await self.session.execute_future(SimpleStatement(query))
        if not rows:
            raise web.HTTPBadRequest(text="Short URL was not found")

        return web.HTTPFound(location=rows[0].long_url)

    async def dice(self, request):
        data = await request.json()
        url_domain = self.config["api"]["short_url_domain"]
        machine_id = self.config["counter"]["machines"][0]

        # Specify validation rule
        DiceRequest = trafaret.Dict({
            trafaret.Key('url'): trafaret.URL
        })

        # Validate received data
        try:
            data = DiceRequest(data)
        except trafaret.DataError:
            raise web.HTTPBadRequest(text="URL is not valid")

        long_url = data["url"]

        # Check if we already have the URL in the database
        query = """
            SELECT short_url FROM long_short WHERE long_url = '%s' LIMIT 1
        """ % long_url

        # We explicitly do not set a consistency level for high availability
        rows = await self.session.execute_future(SimpleStatement(query))

        # If we have already shortened this URL, simply return
        if rows:
            return web.json_response({
                "short_url": "%s/%s" % (url_domain, rows[0].short_url)
            })

        counter_increment = await get_increment(self.session, machine_id)

        if counter_increment == -1:
            raise web.HTTPInternalServerError(text="Something went wrong")

        short_url = base62_encode(counter_increment)

        # A protocol-level batch of operations which are applied atomically
        # By default the batch type is BatchType.LOGGED
        batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
        # Consitency level QUORUM -> (SUM_OF_ALL_REPLICAS / 2 + 1) rounded down

        # Insert data into both tables for easy lookup
        sl_query = self.session.prepare("""
            INSERT INTO short_long (short_url, long_url) VALUES (?, ?)
        """)
        batch.add(sl_query, (short_url, long_url))

        ls_query = self.session.prepare("""
            INSERT INTO long_short (long_url, short_url) VALUES (?, ?)
        """)
        batch.add(ls_query, (long_url, short_url))

        # Execute atomic batch operation asynchronously
        await self.session.execute_future(batch)

        return web.json_response({
            "short_url": "%s/%s" % (url_domain, short_url)
        })
