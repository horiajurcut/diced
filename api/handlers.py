from aiohttp import web


class RoutesHandler:

    def __init__(self):
        pass

    async def index(self, request):
        return web.json_response({"success": True})
