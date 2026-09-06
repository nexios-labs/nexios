import anyio
import pytest

from sillo import SilloApp
from sillo import json, text
from sillo.core.http import HttpContext
from sillo.normalize import NormalizeMiddleware, SlashAction, Normalize
from sillo.testclient import TestClient


class TestNormalizeMiddleware:
    def test_remove_trailing_slash_inline(self):
        app = SilloApp()
        app.use(NormalizeMiddleware(slash_action=SlashAction.REMOVE))

        @app.get("/test")
        async def test_route(ctx: HttpContext):
            return json({"path": ctx.url.path})

        client = TestClient(app)
        response = client.get("/test/")
        assert response.status_code == 200
        assert response.json()["path"] == "/test"

    def test_add_trailing_slash_inline(self):
        app = SilloApp()
        app.use(NormalizeMiddleware(slash_action=SlashAction.ADD))

        @app.get("/test/")
        async def test_route(ctx: HttpContext):
            return json({"path": ctx.url.path})

        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json()["path"] == "/test/"

    def test_double_slash_normalization(self):
        app = SilloApp()
        app.use(NormalizeMiddleware(slash_action=SlashAction.IGNORE))

        @app.get("/api/test")
        async def test_route(ctx: HttpContext):
            return json({"path": ctx.url.path})

        client = TestClient(app)
        response = client.get("/api/test")
        assert response.status_code == 200

    def test_skip_file_extensions(self):
        app = SilloApp()
        app.use(NormalizeMiddleware(slash_action=SlashAction.IGNORE))

        @app.get("/style.css")
        async def css_route(ctx: HttpContext):
            return text("body{}")

        client = TestClient(app)
        response = client.get("/style.css")
        assert response.status_code == 200

    def test_normalize_factory_function(self):
        mw = Normalize(slash_action=SlashAction.ADD, redirect_status_code=308)
        assert isinstance(mw, NormalizeMiddleware)
        assert mw.slash_action == SlashAction.ADD
        assert mw.redirect_status_code == 308

    def test_normalize_case_enabled(self):
        app = SilloApp()
        app.use(NormalizeMiddleware(slash_action=SlashAction.IGNORE, normalize_case=True))

        @app.get("/api/test")
        async def test_route(ctx: HttpContext):
            return json({"path": ctx.url.path})

        client = TestClient(app)
        response = client.get("/API/TEST")
        assert response.status_code == 200

    def test_double_slashes_are_actually_collapsed(self):
        """`auto_remove_double_slashes` has to run into an actual `//` to bite."""
        app = SilloApp()
        app.use(NormalizeMiddleware(slash_action=SlashAction.IGNORE))

        @app.get("/api/test")
        async def test_route(ctx: HttpContext):
            return json({"path": ctx.url.path})

        client = TestClient(app)
        response = client.get("/api//test")
        assert response.status_code == 200
        assert response.json()["path"] == "/api/test"

    def test_redirect_remove_actually_redirects(self):
        app = SilloApp()
        app.use(NormalizeMiddleware(slash_action=SlashAction.REDIRECT_REMOVE))

        @app.get("/test")
        async def test_route(ctx: HttpContext):
            return json({"path": ctx.url.path})

        client = TestClient(app)
        response = client.get("/test/", follow_redirects=False)
        assert response.status_code == 301
        assert response.headers["location"].endswith("/test")

    def test_redirect_add_actually_redirects(self):
        app = SilloApp()
        app.use(
            NormalizeMiddleware(
                slash_action=SlashAction.REDIRECT_ADD, redirect_status_code=308
            )
        )

        @app.get("/test/")
        async def test_route(ctx: HttpContext):
            return json({"path": ctx.url.path})

        client = TestClient(app)
        response = client.get("/test", follow_redirects=False)
        assert response.status_code == 308
        assert response.headers["location"].endswith("/test/")

    def test_non_http_scope_passes_through_untouched(self):
        """Lifespan and websocket scopes are forwarded, never normalized."""
        middleware = NormalizeMiddleware(slash_action=SlashAction.REDIRECT_REMOVE)
        called = {}

        async def downstream(scope, receive, send):
            called["scope"] = scope

        middleware.app = downstream

        async def receive():
            return {"type": "lifespan.startup"}

        async def send(message):
            pass

        anyio.run(
            middleware.__call__, {"type": "lifespan"}, receive, send
        )

        assert called["scope"] == {"type": "lifespan"}

    def test_without_an_inner_app_raises(self):
        middleware = NormalizeMiddleware()

        async def receive():
            return {"type": "http.request"}

        async def send(message):
            pass

        with pytest.raises(RuntimeError, match="without an inner application"):
            anyio.run(
                middleware.__call__,
                {"type": "http", "path": "/x", "method": "GET", "headers": []},
                receive,
                send,
            )
