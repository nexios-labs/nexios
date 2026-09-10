"""Tests for specificity-based route ordering and the ``priority=`` override.

A dynamic route registered before an overlapping literal one used to shadow
it — ``/users/{id}`` declared first would swallow ``/users/me``. The router
now orders routes by path specificity before matching, with an explicit
``priority=`` weight on a route as the manual override, and
``route_order="registration"`` to opt back into the historical behavior.
"""

import pytest

from sillo import SilloApp, json, text
from sillo.core.http import HttpContext
from sillo.core.routing import Route, Router
from sillo.core.routing._utils import route_order_key, route_specificity
from sillo.testclient import TestClient

# ========== route_specificity unit tests ==========


def test_specificity_literal_beats_parameter():
    assert route_specificity("/users/me") < route_specificity("/users/{id}")


def test_specificity_tight_convertor_beats_string_parameter():
    assert route_specificity("/users/{id:int}") < route_specificity("/users/{id}")
    assert route_specificity("/users/{id:int}") < route_specificity("/users/{id:str}")


def test_specificity_string_parameter_beats_wildcard():
    assert route_specificity("/files/{name}") < route_specificity("/files/{path:path}")


def test_specificity_leftmost_segment_decides():
    # literal at position 2 beats a parameter at position 2, regardless of
    # what sits further right
    assert route_specificity("/a/b/{y}") < route_specificity("/a/{x}/c")


def test_specificity_literal_prefix_beats_bare_mount():
    assert route_specificity("/api/health") < route_specificity(
        "/api", trailing_wildcard=True
    )


def test_specificity_mixed_literal_and_param_segment_is_loose():
    # `/v{n}` cannot be parsed as a clean parameter segment -> treated as loose
    assert route_specificity("/v{n}/users") > route_specificity("/{x}/users")


# ========== route_order_key ==========


def test_order_key_priority_dominates_specificity():
    async def h(ctx: HttpContext):
        return text("ok")

    literal = Route("/users/me", h, methods=["GET"])
    dynamic_high = Route("/users/{id}", h, methods=["GET"], priority=10)

    assert route_order_key(dynamic_high) < route_order_key(literal)


# ========== end-to-end dispatch ==========


def test_literal_wins_when_registered_after_dynamic():
    app = SilloApp()

    @app.get("/users/{user_id}")
    async def get_user(ctx: HttpContext, user_id: str):
        return json({"kind": "dynamic", "user_id": user_id})

    @app.get("/users/me")
    async def get_me(ctx: HttpContext):
        return json({"kind": "me"})

    client = TestClient(app)
    assert client.get("/users/me").json() == {"kind": "me"}
    assert client.get("/users/42").json() == {"kind": "dynamic", "user_id": "42"}


def test_tight_convertor_wins_over_string_parameter():
    app = SilloApp()

    @app.get("/items/{name}")
    async def by_name(ctx: HttpContext, name: str):
        return json({"kind": "name", "name": name})

    @app.get("/items/{item_id:int}")
    async def by_id(ctx: HttpContext, item_id: int):
        return json({"kind": "id", "item_id": item_id})

    client = TestClient(app)
    assert client.get("/items/7").json() == {"kind": "id", "item_id": 7}
    assert client.get("/items/socks").json() == {"kind": "name", "name": "socks"}


def test_priority_forces_a_route_ahead():
    app = SilloApp()

    @app.get("/things/special", priority=-10)
    async def demoted(ctx: HttpContext):
        return json({"kind": "literal-demoted"})

    @app.get("/things/{slug}", priority=10)
    async def promoted(ctx: HttpContext, slug: str):
        return json({"kind": "dynamic-promoted", "slug": slug})

    client = TestClient(app)
    # the parameter route was pushed ahead of the literal one on purpose
    assert client.get("/things/special").json() == {
        "kind": "dynamic-promoted",
        "slug": "special",
    }


def test_priority_as_deliberate_fallback():
    app = SilloApp()

    @app.get("/pages/{slug}", priority=-1)
    async def catch_all(ctx: HttpContext, slug: str):
        return json({"kind": "fallback", "slug": slug})

    @app.get("/pages/{slug:int}")
    async def by_number(ctx: HttpContext, slug: int):
        return json({"kind": "numbered", "slug": slug})

    client = TestClient(app)
    assert client.get("/pages/12").json() == {"kind": "numbered", "slug": 12}
    assert client.get("/pages/about").json() == {"kind": "fallback", "slug": "about"}


def test_registration_order_mode_preserves_historical_shadowing():
    app = SilloApp(route_order="registration")

    @app.get("/users/{user_id}")
    async def get_user(ctx: HttpContext, user_id: str):
        return json({"kind": "dynamic", "user_id": user_id})

    @app.get("/users/me")
    async def get_me(ctx: HttpContext):
        return json({"kind": "me"})

    client = TestClient(app)
    # the earlier dynamic route still swallows the later literal one
    assert client.get("/users/me").json() == {"kind": "dynamic", "user_id": "me"}


def test_equal_specificity_keeps_registration_order():
    app = SilloApp()

    @app.get("/a/{x}")
    async def first(ctx: HttpContext, x: str):
        return json({"which": "first", "x": x})

    @app.get("/b/{y}")
    async def second(ctx: HttpContext, y: str):
        return json({"which": "second", "y": y})

    order = [r.raw_path for r in app.router.routes if isinstance(r, Route)]
    # dispatch once so the lazy ordering runs
    TestClient(app).get("/a/1")
    assert [r.raw_path for r in app.router.routes if isinstance(r, Route)] == order


def test_ordering_is_lazy_and_runs_once():
    router = Router()

    async def h(ctx: HttpContext):
        return text("ok")

    router.add_route(Route("/{slug}", h, methods=["GET"]))
    assert router._routes_sorted is False

    router.add_route(Route("/home", h, methods=["GET"]))
    assert router._routes_sorted is False

    router._order_routes()
    assert router._routes_sorted is True
    assert router.routes[0].raw_path == "/home"

    # a later registration re-arms the lazy sort
    router.add_route(Route("/about", h, methods=["GET"]))
    assert router._routes_sorted is False


def test_405_allow_header_still_spans_every_matching_route():
    app = SilloApp()

    @app.post("/reports/{report_id}")
    async def update_report(ctx: HttpContext, report_id: str):
        return json({"updated": report_id})

    @app.get("/reports/summary")
    async def report_summary(ctx: HttpContext):
        return json({"kind": "summary"})

    client = TestClient(app)
    # DELETE matches neither method; the path is claimed by both the literal
    # and the parameter route, and `Allow` must name every method they permit.
    resp = client.delete("/reports/summary")
    assert resp.status_code == 405
    allow = {m.strip() for m in resp.headers["allow"].split(",")}
    assert {"GET", "POST"} <= allow


def test_websocket_routes_are_ordered_by_specificity_too():
    from sillo.websockets import WebSocketContext

    app = SilloApp()

    @app.ws_route("/ws/{room}")
    async def any_room(websocket: WebSocketContext, room: str):
        await websocket.accept()
        await websocket.send_json({"kind": "dynamic", "room": room})
        await websocket.close()

    @app.ws_route("/ws/lobby")
    async def lobby(websocket: WebSocketContext):
        await websocket.accept()
        await websocket.send_json({"kind": "lobby"})
        await websocket.close()

    client = TestClient(app)
    with client.websocket_connect("/ws/lobby") as ws:
        assert ws.receive_json() == {"kind": "lobby"}
    with client.websocket_connect("/ws/other") as ws:
        assert ws.receive_json() == {"kind": "dynamic", "room": "other"}


def test_websocket_priority_override():
    from sillo.websockets import WebSocketContext

    app = SilloApp()

    @app.ws_route("/ws/lobby", priority=-10)
    async def lobby(websocket: WebSocketContext):
        await websocket.accept()
        await websocket.send_json({"kind": "literal-demoted"})
        await websocket.close()

    @app.ws_route("/ws/{room}", priority=10)
    async def any_room(websocket: WebSocketContext, room: str):
        await websocket.accept()
        await websocket.send_json({"kind": "dynamic-promoted", "room": room})
        await websocket.close()

    client = TestClient(app)
    with client.websocket_connect("/ws/lobby") as ws:
        assert ws.receive_json() == {"kind": "dynamic-promoted", "room": "lobby"}


def test_specificity_ordering_across_mounted_router():
    app = SilloApp()
    api = Router(prefix="/api")

    @api.get("/health")
    async def health(ctx: HttpContext):
        return json({"kind": "mounted-health"})

    @app.get("/api/health/raw")
    async def raw_health(ctx: HttpContext):
        return json({"kind": "literal-raw"})

    app.mount_router(api)

    client = TestClient(app)
    assert client.get("/api/health").json() == {"kind": "mounted-health"}
    assert client.get("/api/health/raw").json() == {"kind": "literal-raw"}
