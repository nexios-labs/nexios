"""Host / version routers, constructor middleware, root_path, force_https,
trailing-slash policy, declarative redirects, the route table, and the new
path converters.
"""

import datetime

import pytest

from sillo import SilloApp, json, text
from sillo.core.http import HttpContext
from sillo.core.routing import Router, format_routes, iter_routes
from sillo.testclient import TestClient

# ========== new path converters ==========


@pytest.mark.parametrize(
    "path,url,expected",
    [
        ("/d/{v:date}", "/d/2026-09-10", "2026-09-10"),
        ("/dt/{v:datetime}", "/dt/2026-09-10T13:45:00", "2026-09-10 13:45:00"),
        ("/dt/{v:datetime}", "/dt/2026-09-10T13:45:00Z", "2026-09-10 13:45:00+00:00"),
        ("/b/{v:bool}", "/b/true", "True"),
        ("/b/{v:bool}", "/b/OFF", "False"),
        ("/u/{v:ulid}", "/u/01ARZ3NDEKTSV4RRFFQ69G5FAV", "01ARZ3NDEKTSV4RRFFQ69G5FAV"),
        ("/a/{v:alpha}", "/a/Hello", "Hello"),
        ("/n/{v:alnum}", "/n/AB12cd", "AB12cd"),
    ],
)
def test_new_converters_bind_and_coerce(path, url, expected):
    app = SilloApp()

    @app.get(path)
    async def h(ctx: HttpContext, v):
        return json({"v": str(v)})

    assert TestClient(app).get(url).json() == {"v": expected}


def test_date_converter_yields_a_date_object():
    app = SilloApp()

    @app.get("/d/{v:date}")
    async def h(ctx: HttpContext, v):
        return json({"type": type(v).__name__, "year": v.year})

    body = TestClient(app).get("/d/2026-09-10").json()
    assert body == {"type": "date", "year": 2026}


def test_bool_converter_rejects_non_bool_words():
    app = SilloApp()

    @app.get("/b/{v:bool}")
    async def h(ctx: HttpContext, v):
        return json({"v": v})

    assert TestClient(app).get("/b/maybe").status_code == 404


def test_alpha_converter_does_not_swallow_digits():
    app = SilloApp()

    @app.get("/t/{v:alpha}")
    async def h(ctx: HttpContext, v):
        return json({"v": v})

    assert TestClient(app).get("/t/abc123").status_code == 404


def test_converter_round_trips_through_url_for():
    app = SilloApp()

    @app.get("/reports/{day:date}", name="report")
    async def h(ctx: HttpContext, day):
        return text("ok")

    url = app.url_for("report", day=datetime.date(2026, 1, 2))
    assert str(url) == "/reports/2026-01-02"


# ========== Router(host=...) ==========


def _mounted(app: SilloApp, sub: Router) -> SilloApp:
    app.mount_router(sub)
    return app


def test_host_router_only_answers_its_host():
    app = SilloApp()
    admin = Router(prefix="/admin", host="admin.example.com")

    @admin.get("/")
    async def index(ctx: HttpContext):
        return json({"area": "admin"})

    _mounted(app, admin)
    client = TestClient(app)

    assert client.get("/admin/").status_code == 404
    assert client.get("/admin/", headers={"host": "admin.example.com"}).json() == {
        "area": "admin"
    }


def test_host_router_wildcard_matches_one_label():
    app = SilloApp()
    tenants = Router(prefix="/t", host="*.app.example.com")

    @tenants.get("/me")
    async def me(ctx: HttpContext):
        return json({"ok": True})

    _mounted(app, tenants)
    client = TestClient(app)

    assert (
        client.get("/t/me", headers={"host": "acme.app.example.com"}).status_code == 200
    )
    assert (
        client.get("/t/me", headers={"host": "a.b.app.example.com"}).status_code == 404
    )
    assert client.get("/t/me", headers={"host": "app.example.com"}).status_code == 404


# ========== Router(version=...) ==========


def test_version_router_selected_by_header():
    app = SilloApp()
    v1 = Router(prefix="/items", version="1")
    v2 = Router(prefix="/items", version="2")

    @v1.get("/x")
    async def x1(ctx: HttpContext):
        return json({"v": 1})

    @v2.get("/x")
    async def x2(ctx: HttpContext):
        return json({"v": 2})

    app.mount_router(v1)
    app.mount_router(v2)
    client = TestClient(app)

    assert client.get("/items/x", headers={"X-API-Version": "1"}).json() == {"v": 1}
    assert client.get("/items/x", headers={"X-API-Version": "2"}).json() == {"v": 2}
    assert client.get("/items/x").status_code == 404


def test_version_router_selected_by_accept_parameter():
    app = SilloApp()
    v2 = Router(prefix="/items", version="2")

    @v2.get("/x")
    async def x2(ctx: HttpContext):
        return json({"v": 2})

    app.mount_router(v2)
    resp = TestClient(app).get(
        "/items/x", headers={"Accept": "application/json; version=2"}
    )
    assert resp.json() == {"v": 2}


# ========== Router(middleware=[...]) ==========


def test_router_constructor_middleware_runs():
    seen: list[str] = []

    class Mark:
        def __init__(self, app, tag):
            self.app = app
            self.tag = tag

        async def __call__(self, scope, receive, send):
            seen.append(self.tag)
            await self.app(scope, receive, send)

    app = SilloApp()
    sub = Router(prefix="/s", middleware=[(Mark, ("a",), {}), (Mark, ("b",), {})])

    @sub.get("/")
    async def h(ctx: HttpContext):
        return text("ok")

    app.mount_router(sub)
    assert TestClient(app).get("/s/").status_code == 200
    assert seen == ["a", "b"]


# ========== SilloApp(root_path=...) ==========


def test_root_path_folds_prefix_into_scope_and_strips_it_from_path():
    app = SilloApp(root_path="/api")

    @app.get("/ping")
    async def ping(ctx: HttpContext):
        return json(
            {"root_path": ctx.scope.get("root_path"), "path": ctx.scope["path"]}
        )

    body = TestClient(app).get("/api/ping").json()
    assert body["root_path"] == "/api"
    assert body["path"] == "/ping"


def test_root_path_makes_url_for_absolute_to_the_mount():
    app = SilloApp(root_path="/api")

    @app.get("/things/{n:int}", name="thing")
    async def thing(ctx: HttpContext, n: int):
        return json({"url": str(ctx.url_for("thing", n=n))})

    assert TestClient(app).get("/api/things/3").json() == {"url": "/api/things/3"}


# ========== SilloApp(force_https=...) ==========


def test_force_https_redirects_plain_http():
    app = SilloApp(force_https=True)

    @app.get("/x")
    async def x(ctx: HttpContext):
        return text("ok")

    resp = TestClient(app).get("/x?a=1", follow_redirects=False)
    assert resp.status_code == 308
    assert resp.headers["location"] == "https://testserver/x?a=1"


def test_force_https_trusts_forwarded_proto():
    app = SilloApp(force_https=True)

    @app.get("/x")
    async def x(ctx: HttpContext):
        return text("ok")

    resp = TestClient(app).get(
        "/x", headers={"X-Forwarded-Proto": "https"}, follow_redirects=False
    )
    assert resp.status_code == 200


# ========== trailing_slash ==========


def test_trailing_slash_strict_is_the_default():
    app = SilloApp()

    @app.get("/a")
    async def a(ctx: HttpContext):
        return text("a")

    assert TestClient(app).get("/a/").status_code == 404


def test_trailing_slash_redirect():
    app = SilloApp(trailing_slash="redirect")

    @app.get("/a")
    async def a(ctx: HttpContext):
        return text("a")

    @app.post("/b/")
    async def b(ctx: HttpContext):
        return text("b")

    client = TestClient(app)

    r = client.get("/a/", follow_redirects=False)
    assert r.status_code == 308 and r.headers["location"] == "/a"

    r = client.post("/b", follow_redirects=False)
    assert r.status_code == 308 and r.headers["location"] == "/b/"


def test_trailing_slash_ignore_serves_in_place():
    app = SilloApp(trailing_slash="ignore")

    @app.get("/a")
    async def a(ctx: HttpContext):
        return json({"hit": "a"})

    assert TestClient(app).get("/a/").json() == {"hit": "a"}


def test_trailing_slash_redirect_keeps_query_and_root_path():
    app = SilloApp(root_path="/api", trailing_slash="redirect")

    @app.get("/a")
    async def a(ctx: HttpContext):
        return text("a")

    r = TestClient(app).get("/api/a/?x=1", follow_redirects=False)
    assert r.status_code == 308
    assert r.headers["location"] == "/api/a?x=1"


# ========== declarative redirect ==========


def test_declarative_redirect_static():
    app = SilloApp()
    app.redirect("/old", "/new")

    @app.get("/new")
    async def new(ctx: HttpContext):
        return text("new")

    r = TestClient(app).get("/old", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == "/new"


def test_declarative_redirect_interpolates_params_and_query():
    app = SilloApp()
    app.redirect("/u/{user_id}", "/users/{user_id}", status_code=301)

    r = TestClient(app).get("/u/42?tab=posts", follow_redirects=False)
    assert r.status_code == 301
    assert r.headers["location"] == "/users/42?tab=posts"


def test_declarative_redirect_is_hidden_from_schema():
    app = SilloApp()
    app.redirect("/old", "/new")
    paths = app.build_openapi()
    assert "/old" not in paths


def test_declarative_redirect_carries_root_path():
    app = SilloApp(root_path="/api")
    app.redirect("/old", "/new")

    r = TestClient(app).get("/api/old", follow_redirects=False)
    assert r.headers["location"] == "/api/new"


# ========== print_routes / iter_routes ==========


def test_iter_routes_flattens_prefixes_and_mounts():
    app = SilloApp()

    @app.get("/top")
    async def top(ctx: HttpContext):
        return text("t")

    sub = Router(prefix="/sub")

    @sub.get("/leaf")
    async def leaf(ctx: HttpContext):
        return text("l")

    @sub.ws_route("/ws")
    async def ws(ctx):
        await ctx.accept()
        await ctx.close()

    app.mount_router(sub)

    rows = iter_routes(app.router)
    by_path = {r.path: r for r in rows}

    assert "/top" in by_path and by_path["/top"].kind == "http"
    assert "/sub/*" in by_path and by_path["/sub/*"].kind == "mount"
    assert "/sub/leaf" in by_path
    assert by_path["/sub/ws"].kind == "websocket"


def test_format_routes_is_a_string_table():
    app = SilloApp()

    @app.get("/hello", name="hello")
    async def hello(ctx: HttpContext):
        return text("hi")

    table = format_routes(app.router)
    assert "/hello" in table
    assert "(hello)" in table
    assert "GET" in table


def test_print_routes_writes_to_stdout(capsys):
    app = SilloApp()

    @app.get("/hi")
    async def hi(ctx: HttpContext):
        return text("hi")

    app.print_routes()
    out = capsys.readouterr().out
    assert "/hi" in out


def test_format_routes_on_empty_router():
    assert format_routes(Router()) == "(no routes registered)"


# ========== converter to_string (url_for reverse) ==========


@pytest.mark.parametrize(
    "conv,value,expected",
    [
        ("bool", True, "true"),
        ("bool", False, "false"),
        (
            "datetime",
            datetime.datetime(2026, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
            "2026-01-02T03:04:05+00:00",
        ),
        ("ulid", "01arz3ndektsv4rrffq69g5fav", "01ARZ3NDEKTSV4RRFFQ69G5FAV"),
        ("alpha", "abc", "abc"),
        ("alnum", "a1b2", "a1b2"),
    ],
)
def test_converter_to_string_round_trips(conv, value, expected):
    app = SilloApp()

    @app.get("/x/{v:" + conv + "}", name="x")
    async def h(ctx: HttpContext, v):
        return text("ok")

    assert str(app.url_for("x", v=value)).rsplit("/", 1)[-1] == expected


def test_request_host_falls_back_to_server_when_no_host_header():
    from sillo.core.routing._utils import request_host

    scope = {"type": "http", "headers": [], "server": ("box.local", 8000)}
    assert request_host(scope) == "box.local"


def test_ulid_converter_to_string_rejects_a_bad_value():
    from sillo.core.converters import CONVERTOR_TYPES

    with pytest.raises(ValueError):
        CONVERTOR_TYPES["ulid"].to_string("not-a-ulid")


def test_endpoint_name_is_empty_for_a_missing_handler():
    from sillo.core.routing.introspect import _endpoint_name

    assert _endpoint_name(None) == ""


def test_format_routes_labels_a_mount_row():
    app = SilloApp()
    sub = Router(prefix="/area")

    @sub.get("/x")
    async def x(ctx: HttpContext):
        return text("x")

    app.mount_router(sub)
    table = format_routes(app.router)
    assert "MOUNT" in table
    assert "/area/*" in table


def test_router_print_routes_takes_a_file(tmp_path):
    app = SilloApp()

    @app.get("/z")
    async def z(ctx: HttpContext):
        return text("z")

    out = tmp_path / "routes.txt"
    with out.open("w") as fh:
        app.router.print_routes(file=fh)
    assert "/z" in out.read_text()


def test_declarative_redirect_can_drop_the_query_and_take_more_methods():
    app = SilloApp()
    app.redirect("/legacy", "/current", methods=("GET", "POST"), include_query=False)

    client = TestClient(app)
    r = client.get("/legacy?keep=me", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == "/current"

    r = client.post("/legacy", follow_redirects=False)
    assert r.status_code == 307


def test_trailing_slash_ignore_reaches_a_mounted_route():
    app = SilloApp(trailing_slash="ignore")
    sub = Router(prefix="/sub")

    @sub.get("/leaf")
    async def leaf(ctx: HttpContext):
        return json({"hit": True})

    app.mount_router(sub)
    assert TestClient(app).get("/sub/leaf/").json() == {"hit": True}


def test_trailing_slash_redirect_leaves_the_root_alone():
    app = SilloApp(trailing_slash="redirect")

    @app.get("/only")
    async def only(ctx: HttpContext):
        return text("ok")

    # "/" toggles to "" which is refused, so a bare "/" still 404s cleanly
    assert TestClient(app).get("/").status_code == 404


async def test_https_redirect_uses_server_when_no_host_header():
    from sillo.application import _https_redirect

    sent: list = []

    async def send(msg):
        sent.append(msg)

    scope = {
        "type": "http",
        "headers": [],
        "server": ("box.local", 8443),
        "path": "/p",
        "query_string": b"",
        "root_path": "",
    }
    await _https_redirect(scope, send)
    start = sent[0]
    assert start["status"] == 308
    loc = dict(start["headers"])[b"location"]
    assert loc == b"https://box.local:8443/p"


def test_host_router_refuses_a_websocket_from_the_wrong_host():
    app = SilloApp()
    live = Router(prefix="/ws", host="live.example.com")

    @live.ws_route("/feed")
    async def feed(ctx):
        await ctx.accept()
        await ctx.send_json({"ok": True})
        await ctx.close()

    app.mount_router(live)
    client = TestClient(app)

    from sillo.websockets.base import WebSocketDisconnect

    with client.websocket_connect(
        "/ws/feed", headers={"host": "live.example.com"}
    ) as ws:
        assert ws.receive_json() == {"ok": True}

    with pytest.raises(WebSocketDisconnect) as caught:  # noqa: SIM117
        with client.websocket_connect("/ws/feed") as ws:
            ws.receive_json()
    assert caught.value.code == 4404


def test_trailing_slash_redirect_falls_through_on_a_method_mismatch():
    app = SilloApp(trailing_slash="redirect")

    @app.post("/submit")
    async def submit(ctx: HttpContext):
        return text("ok")

    # GET /submit/ toggles to /submit, which exists but only for POST -> no
    # trailing-slash redirect, the request 404s rather than 405/308
    assert TestClient(app).get("/submit/", follow_redirects=False).status_code == 404


def test_version_router_matches_when_only_host_is_also_set():
    app = SilloApp()
    r = Router(prefix="/x", host="h.example.com", version="9")

    @r.get("/y")
    async def y(ctx: HttpContext):
        return text("y")

    app.mount_router(r)
    client = TestClient(app)

    ok = client.get("/x/y", headers={"host": "h.example.com", "X-API-Version": "9"})
    assert ok.status_code == 200
    # right host, wrong version
    assert client.get("/x/y", headers={"host": "h.example.com"}).status_code == 404
