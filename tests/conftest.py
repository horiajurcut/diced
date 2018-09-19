import asyncio
import pytest

from api.runner import init


@pytest.fixture
async def server(loop, aiohttp_server):
    app, _, _ = await init(loop)
    return await aiohttp_server(app)


@pytest.fixture
async def client(server, aiohttp_client):
    return await aiohttp_client(server)
