import random
import trafaret

from aiohttp import web
from api.utils import encode as base62_encode
from cassandra import ConsistencyLevel
from cassandra.query import BatchStatement


class RoutesHandler:

    def __init__(self, session, config):
        self.session = session
        self.config = config

    async def index(self, request):
        return web.json_response({
            "success": True,
            "message": "DICED - The fancy URL Shortener"
        })

    async def redirect(self, request):
        short_url = request.match_info["short_url"]

        query = self.session.prepare("""
            SELECT long_url FROM short_long WHERE short_url = '%s' LIMIT 1
        """ % short_url)

        rows = await self.session.execute_future(query)
        if not rows:
            raise web.HTTPBadRequest(text="Short URL was not found")

        return web.json_response({
            "long_url": rows[0].long_url
        })

    async def dice(self, request):
        data = await request.json()

        # Specify validation rule
        DiceRequest = trafaret.Dict({
            trafaret.Key('url'): trafaret.URL
        })

        # Validate received data
        try:
            data = DiceRequest(data)
        except trafaret.DataError:
            raise web.HTTPBadRequest(text="URL is not valid")

        long_url = data['url']
        short_url = base62_encode(random.randint(1, 999999))

        # A protocol-level batch of operations which are applied atomically
        # by default - BatchType.LOGGED
        batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
        # Consitency level QUORUM -> (SUM OF ALL REPLICAS / 2 + 1) rounded down

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
            "short_url": "%s/%s" % (self.config["api"]["short_url_domain"], short_url)
        })
