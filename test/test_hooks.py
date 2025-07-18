import asyncio
import types

import pytest

from nexios.hooks import after_request, before_request


class DummyReq:
    def __init__(self, method="GET", path="/test"):
        self.method = method
        self.url = types.SimpleNamespace(path=path)


class DummyRes:
    pass


@pytest.mark.asyncio
async def test_before_request_hook_called():
    called = {}

    async def hook(req, res):
        called["before"] = True

    @before_request(hook)
    async def handler(req, res):
        called["handler"] = True
        return 42

    req = DummyReq()
    res = DummyRes()
    result = await handler(req, res)
    assert called["before"]
    assert called["handler"]
    assert result == 42


@pytest.mark.asyncio
async def test_after_request_hook_called():
    called = {}

    async def hook(req, res):
        called["after"] = True

    @after_request(hook)
    async def handler(req, res):
        called["handler"] = True
        return 99

    req = DummyReq()
    res = DummyRes()
    result = await handler(req, res)
    assert called["handler"]
    assert called["after"]
    assert result == 99
