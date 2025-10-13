import asyncio
from pathlib import Path

import pytest

from nexios import NexiosApp
from nexios.static import StaticFiles
from nexios.testing.client import Client


@pytest.mark.asyncio
async def test_static_file_serving():
    app = NexiosApp()
    static_dir = Path(__file__).parent / "static"
    app.register(StaticFiles(directory=static_dir), "/static")

    async with Client(app) as client:
        # Test existing file
        resp = await client.get("/static/example.txt")
        assert resp.status_code == 200
        assert b"welcome to nexios" in resp.content

        # Test missing file
        resp = await client.get("/static/doesnotexist.txt")
        assert resp.status_code == 404
