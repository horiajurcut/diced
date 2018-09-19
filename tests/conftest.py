import asyncio
import pytest

from api.runner import init


@pytest.fixture
async def client(loop, aiohttp_client):
    app, _, _ = await init(loop)
    return await aiohttp_client(app)
