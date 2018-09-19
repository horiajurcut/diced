import random
import trafaret

from aiohttp import web
from api.utils import encode as base62_encode


class RoutesHandler:

    def __init__(self, db_store, config):
        self.db_store = db_store
        self.config = config

    async def index(self, request):
        return web.json_response({
            "message": "dice.it - The Fancy URL Shortener"
        })

    async def redirect(self, request):
        short_url = request.match_info["short_url"]

        rows = await self.db_store.get_long_url(short_url)
        if not rows:
            raise web.HTTPBadRequest(text="Short URL was not found")

        return web.HTTPFound(location=rows[0].long_url)

    async def dice(self, request):
        data = await request.json()
        url_domain = self.config["api"]["short_url_domain"]

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
        rows = await self.db_store.get_short_url(long_url)

        # If we have already shortened this URL, simply return
        if rows:
            return web.json_response({
                "short_url": "%s/%s" % (url_domain, rows[0].short_url)
            })

        counter_increment = await self.db_store.get_increment()

        if counter_increment == -1:
            raise web.HTTPInternalServerError(text="Something went wrong")

        short_url = base62_encode(counter_increment)

        # Update cassandra tables
        await self.db_store.batch_update(short_url, long_url)

        return web.json_response({
            "short_url": "%s/%s" % (url_domain, short_url)
        })
