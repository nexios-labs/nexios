import asyncio
import types

import pytest

from nexios.http import Request, Response
from nexios.views import APIView


class DummyRequest:
    def __init__(self, method="GET"):
        self.method = method
        self.url = types.SimpleNamespace(path="/test")


class DummyResponse:
    def __init__(self):
        self._status_code = 200
        self._json = None

    def status(self, code):
        self._status_code = code
        return self

    def json(self, data):
        self._json = data
        return self


@pytest.mark.asyncio
async def test_api_view_get_default():
    view = APIView()
    req = DummyRequest("GET")
    res = DummyResponse()
    response = await view.get(req, res)
    assert response._status_code == 404
    assert response._json == {"error": "Not Found"}


@pytest.mark.asyncio
async def test_api_view_method_not_allowed():
    view = APIView()
    req = DummyRequest("OPTIONS")
    res = DummyResponse()
    response = await view.method_not_allowed(req, res)
    assert response._status_code == 405
    assert response._json == {"error": "Method Not Allowed"}


@pytest.mark.asyncio
async def test_api_view_dispatch_calls_correct_method():
    class MyView(APIView):
        async def get(self, req, res):
            return res.status(200).json({"ok": True})

    view = MyView()
    req = DummyRequest("GET")
    res = DummyResponse()
    response = await view.dispatch(req, res)
    assert response._status_code == 200
    assert response._json == {"ok": True}


@pytest.mark.asyncio
async def test_api_view_dispatch_error_handler():
    class MyView(APIView):
        async def get(self, req, res):
            raise ValueError("fail")

    called = {}

    async def handler(req, res, exc):
        called["handled"] = True
        return res.status(400).json({"error": str(exc)})

    MyView.error_handlers = {ValueError: handler}
    view = MyView()
    req = DummyRequest("GET")
    res = DummyResponse()
    response = await view.dispatch(req, res)
    assert response._status_code == 400
    assert response._json == {"error": "fail"}
    assert called["handled"]
