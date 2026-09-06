"""
Content negotiation middleware and the per-request Accepts helpers.

The negotiation functions themselves are covered in test_accepts_negotiation;
this exercises them through a live request, including the strict variant that
rejects clients it cannot satisfy with a 406.
"""

import pytest

from sillo import SilloApp
from sillo import json
from sillo.http.accepts import (
    Accepts,
    AcceptsInfo,
    AcceptsMiddleware,
    ContentNegotiationMiddleware,
    StrictContentNegotiationMiddleware,
    get_accepted_content_types,
    get_accepted_charsets,
    get_accepted_encodings,
    get_accepted_languages,
    get_accepts_from_request,
    get_accepts_info,
    get_best_accepted_content_type,
    get_best_accepted_language,
)
from sillo.testclient import TestClient


# ── AcceptsInfo over a live request ──────────────────────────────────────


@pytest.fixture
def client():
    app = SilloApp()

    @app.get("/info")
    async def info(ctx):
        return json(get_accepts_info(ctx))

    @app.get("/types")
    async def types(ctx):
        return json(
            {
                "types": get_accepted_content_types(ctx),
                "languages": get_accepted_languages(ctx),
                "charsets": get_accepted_charsets(ctx),
                "encodings": get_accepted_encodings(ctx),
            }
        )

    @app.get("/best")
    async def best(ctx):
        return json(
            {
                "type": get_best_accepted_content_type(
                    ctx, ["application/json", "text/html"]
                ),
                "language": get_best_accepted_language(ctx, ["en", "fr"]),
            }
        )

    @app.get("/wrapper")
    async def wrapper(ctx):
        accepts = get_accepts_from_request(ctx)
        return json({"has_accepts": accepts is not None})

    # These helpers read state the middleware attaches to the request.
    app.use(AcceptsMiddleware())
    return TestClient(app)


def test_accepts_info_is_a_dict(client):
    resp = client.get("/info", headers={"Accept": "application/json"})
    assert isinstance(resp.json(), dict)


def test_accepted_types_are_listed(client):
    resp = client.get(
        "/types",
        headers={
            "Accept": "application/json, text/html;q=0.8",
            "Accept-Language": "en, fr;q=0.5",
            "Accept-Charset": "utf-8",
            "Accept-Encoding": "gzip",
        },
    )
    data = resp.json()
    assert "application/json" in data["types"]
    assert "en" in data["languages"]


def test_missing_accept_headers_yield_empty_lists(client):
    data = client.get("/types").json()
    assert isinstance(data["types"], list)


def test_best_match_through_a_request(client):
    resp = client.get(
        "/best",
        headers={"Accept": "text/html", "Accept-Language": "fr"},
    )
    data = resp.json()
    assert data["type"] == "text/html"
    assert data["language"] == "fr"


def test_best_match_falls_back_when_nothing_matches(client):
    """Neither the type nor the language is one the server offers, so both
    fall back to the first option -- there is always something to answer with."""
    resp = client.get(
        "/best",
        headers={"Accept": "text/csv", "Accept-Language": "de"},
    )
    data = resp.json()
    assert data["type"] == "application/json"
    assert data["language"] == "en"


def test_best_match_matches_a_language_region_prefix(client):
    resp = client.get("/best", headers={"Accept-Language": "en-GB"})
    assert resp.json()["language"] == "en"


def test_best_match_matches_a_server_side_region_variant():
    """A server offering `en-US` satisfies a client that only asked for `en`."""
    app = SilloApp()
    app.use(AcceptsMiddleware())

    @app.get("/best-region")
    async def best_region(ctx):
        return json({"language": get_best_accepted_language(ctx, ["en-US", "fr"])})

    client = TestClient(app)
    resp = client.get("/best-region", headers={"Accept-Language": "en-GB"})
    assert resp.json()["language"] == "en-US"


def test_the_accepts_wrapper_is_available(client):
    assert client.get("/wrapper").json()["has_accepts"] is True


# ── AcceptsInfo directly ─────────────────────────────────────────────────


def test_accepts_info_exposes_each_header():
    app = SilloApp()
    captured = {}

    @app.get("/x")
    async def x(ctx):
        info = AcceptsInfo(ctx)
        captured["accept"] = info.accept
        captured["language"] = info.accept_language
        captured["charset"] = info.accept_charset
        captured["encoding"] = info.accept_encoding
        captured["types"] = info.get_accepted_types()
        captured["languages"] = info.get_accepted_languages()
        captured["charsets"] = info.get_accepted_charsets()
        captured["encodings"] = info.get_accepted_encodings()
        return json({})

    app.use(AcceptsMiddleware())
    TestClient(app).get(
        "/x",
        headers={
            "Accept": "application/json",
            "Accept-Language": "en",
            "Accept-Charset": "utf-8",
            "Accept-Encoding": "gzip",
        },
    )

    # With the middleware installed, `accept` is the parsed header rather
    # than the raw string.
    assert [i.value for i in captured["accept"]] == ["application/json"]
    assert "application/json" in captured["types"]
    assert "en" in captured["languages"]
    assert "utf-8" in captured["charsets"]
    assert "gzip" in captured["encodings"]


# ── AcceptsMiddleware ────────────────────────────────────────────────────


def _app_with(middleware):
    app = SilloApp()

    @app.get("/x")
    async def x(ctx):
        return json({"ok": True})

    app.use(middleware)
    return TestClient(app)


def test_accepts_middleware_passes_requests_through():
    client = _app_with(AcceptsMiddleware())
    assert client.get("/x", headers={"Accept": "application/json"}).status_code == 200


def test_accepts_middleware_sets_vary():
    client = _app_with(AcceptsMiddleware(set_vary_header=True))
    resp = client.get("/x", headers={"Accept": "application/json"})
    assert "vary" in {k.lower() for k in resp.headers}


def test_accepts_middleware_can_omit_vary():
    client = _app_with(AcceptsMiddleware(set_vary_header=False))
    assert client.get("/x").status_code == 200


def test_accepts_middleware_with_custom_defaults():
    client = _app_with(
        AcceptsMiddleware(
            default_content_type="text/html",
            default_language="fr",
            default_charset="iso-8859-1",
        )
    )
    assert client.get("/x").status_code == 200


def test_accepts_middleware_without_an_accept_header():
    client = _app_with(AcceptsMiddleware())
    assert client.get("/x").status_code == 200


def test_negotiates_content_type_when_the_response_has_none():
    """`apply_headers` only fills in Content-Type when the response left it blank."""
    from sillo.core.http.response import BaseResponse

    app = SilloApp()

    @app.get("/x")
    async def x(ctx):
        return BaseResponse(body=b"data", content_type=None)

    app.use(AcceptsMiddleware(default_content_type="text/csv"))
    client = TestClient(app)

    response = client.get("/x", headers={"Accept": "text/csv"})
    assert response.headers["content-type"] == "text/csv"


def test_falls_back_to_the_default_content_type_without_an_accept_header():
    """No `Accept` header at all -- not even `*/*`, which a real HTTP client
    always sends, and which would take the *other* branch (negotiating `*/*`
    against the default, landing on the same value through a different
    path). Driven at the ASGI level directly so the request can omit it."""
    import anyio

    from sillo.core.http.response import BaseResponse

    app = SilloApp()

    @app.get("/x")
    async def x(ctx):
        return BaseResponse(body=b"data", content_type=None)

    app.use(AcceptsMiddleware(default_content_type="application/xml"))

    sent: list[dict] = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/x",
        "headers": [],
        "query_string": b"",
    }

    anyio.run(app, scope, receive, send)

    start = next(m for m in sent if m["type"] == "http.response.start")
    headers = {k.decode(): v.decode() for k, v in start["headers"]}
    assert headers["content-type"] == "application/xml"


def test_non_http_scope_passes_through_untouched():
    middleware = AcceptsMiddleware()
    called = {}

    async def downstream(scope, receive, send):
        called["scope"] = scope

    middleware.app = downstream

    async def receive():
        return {"type": "lifespan.startup"}

    async def send(message):
        pass

    import anyio

    anyio.run(middleware.__call__, {"type": "lifespan"}, receive, send)

    assert called["scope"] == {"type": "lifespan"}


def test_without_an_inner_app_raises():
    import anyio

    middleware = AcceptsMiddleware()

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


# ── ContentNegotiationMiddleware ─────────────────────────────────────────


def test_content_negotiation_passes_requests_through():
    client = _app_with(ContentNegotiationMiddleware())
    assert client.get("/x", headers={"Accept": "application/json"}).status_code == 200


def test_content_negotiation_with_a_wildcard():
    client = _app_with(ContentNegotiationMiddleware())
    assert client.get("/x", headers={"Accept": "*/*"}).status_code == 200


# ── StrictContentNegotiationMiddleware ───────────────────────────────────


def test_strict_negotiation_accepts_a_supported_type():
    client = _app_with(
        StrictContentNegotiationMiddleware(available_types=["application/json"])
    )
    assert client.get("/x", headers={"Accept": "application/json"}).status_code == 200


def test_strict_negotiation_rejects_an_unsupported_type():
    """A client that cannot consume any representation we offer gets 406.

    Note the endpoint must not offer the default content type, or negotiation
    falls back onto it and the request is served after all.
    """
    client = _app_with(StrictContentNegotiationMiddleware(available_types=["text/csv"]))
    resp = client.get("/x", headers={"Accept": "application/xml"})
    assert resp.status_code == 406
    assert "text/csv" in resp.text


def test_strict_negotiation_honours_a_wildcard():
    client = _app_with(
        StrictContentNegotiationMiddleware(available_types=["application/json"])
    )
    assert client.get("/x", headers={"Accept": "*/*"}).status_code == 200


def test_strict_negotiation_checks_language_too():
    client = _app_with(
        StrictContentNegotiationMiddleware(
            available_types=["application/json"], available_languages=["en"]
        )
    )
    resp = client.get(
        "/x", headers={"Accept": "application/json", "Accept-Language": "en"}
    )
    assert resp.status_code == 200


def test_strict_negotiation_with_no_accept_header():
    client = _app_with(
        StrictContentNegotiationMiddleware(available_types=["application/json"])
    )
    assert client.get("/x").status_code in (200, 406)


def test_strict_negotiation_non_http_scope_passes_through_untouched():
    middleware = StrictContentNegotiationMiddleware(available_types=["application/json"])
    called = {}

    async def downstream(scope, receive, send):
        called["scope"] = scope

    middleware.app = downstream

    async def receive():
        return {"type": "lifespan.startup"}

    async def send(message):
        pass

    import anyio

    anyio.run(middleware.__call__, {"type": "lifespan"}, receive, send)

    assert called["scope"] == {"type": "lifespan"}


def test_negotiated_values_reach_the_handler():
    """The route handler gets its own, separately-built HttpContext.

    The negotiated values used to be set as a plain attribute on the
    middleware's own context object, which the handler's context never saw
    -- so this reads them the way a handler actually would, off ctx.state,
    not off the object the middleware happened to negotiate against.
    """
    app = SilloApp()

    @app.get("/x")
    async def x(ctx):
        return json(
            {
                "type": ctx.state.negotiated_content_type,
                "lang": ctx.state.negotiated_language,
            }
        )

    app.use(
        StrictContentNegotiationMiddleware(
            available_types=["application/json"], available_languages=["en"]
        )
    )
    client = TestClient(app)

    response = client.get(
        "/x", headers={"Accept": "application/json", "Accept-Language": "en"}
    )

    assert response.json() == {"type": "application/json", "lang": "en"}


# ── the Accepts factory ──────────────────────────────────────────────────


def test_accepts_factory_builds_a_middleware():
    assert Accepts() is not None


def test_accepts_factory_takes_defaults():
    assert Accepts(default_content_type="text/html", default_language="fr") is not None
