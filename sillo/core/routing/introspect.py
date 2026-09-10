"""Walk a router tree and describe every route it can reach.

The router keeps routes in a flat list per node, with mounted sub-routers held
inside :class:`~sillo.core.routing.grouping.Group` objects. Reading a whole
application off that shape — for a startup log, a ``sillo routes`` command, or a
test that asserts what got registered — means recursing through the groups and
carrying each one's prefix down. That recursion lives here so the router class
does not grow a second traversal next to ``get_all_routes``.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import IO, Any


@dataclass(frozen=True, slots=True)
class RouteInfo:
    """One matchable endpoint, with its prefix already folded into ``path``."""

    methods: tuple[str, ...]
    path: str
    name: str | None
    endpoint: str
    kind: str  # "http" | "websocket" | "mount"


def _endpoint_name(handler: Any) -> str:
    if handler is None:
        return ""
    module = getattr(handler, "__module__", "") or ""
    qualname = getattr(handler, "__qualname__", None) or getattr(
        handler, "__name__", None
    )
    if qualname is None:
        qualname = type(handler).__name__
    return f"{module}.{qualname}" if module else str(qualname)


def iter_routes(router: Any, *, prefix: str = "") -> list[RouteInfo]:
    """Return every route reachable from ``router``, prefixes resolved.

    HTTP routes, WebSocket routes and mounted sub-applications are all
    included; a mount is reported once as ``kind="mount"`` and then descended
    into. Order follows the router's own list order (which is match order).
    """
    from .grouping import Group
    from .router import Route
    from .websocket import WebsocketRoute

    out: list[RouteInfo] = []
    for route in getattr(router, "routes", []):
        raw = getattr(route, "raw_path", "") or ""
        full = (prefix + raw) or "/"

        if isinstance(route, Route):
            methods = tuple(sorted(m for m in (getattr(route, "methods", None) or ())))
            out.append(
                RouteInfo(
                    methods=methods,
                    path=full,
                    name=getattr(route, "name", None),
                    endpoint=_endpoint_name(getattr(route, "handler", None)),
                    kind="http",
                )
            )
        elif isinstance(route, WebsocketRoute):
            out.append(
                RouteInfo(
                    methods=("WEBSOCKET",),
                    path=full,
                    name=getattr(route, "name", None),
                    endpoint=_endpoint_name(getattr(route, "handler", None)),
                    kind="websocket",
                )
            )
        elif isinstance(route, Group):
            mount_path = (prefix + (getattr(route, "path", "") or "")) or "/"
            out.append(
                RouteInfo(
                    methods=(),
                    path=mount_path + "/*",
                    name=getattr(route, "name", None),
                    endpoint=_endpoint_name(getattr(route, "_base_app", None))
                    or type(getattr(route, "_base_app", route)).__name__,
                    kind="mount",
                )
            )
            inner = getattr(route, "_base_app", None)
            if hasattr(inner, "routes"):
                out.extend(iter_routes(inner, prefix=mount_path))
        else:  # a bare ASGI app or custom BaseRoute — report what we can
            out.append(
                RouteInfo(
                    methods=(),
                    path=full,
                    name=getattr(route, "name", None),
                    endpoint=type(route).__name__,
                    kind="mount",
                )
            )
    return out


def format_routes(router: Any, *, prefix: str = "") -> str:
    """Render :func:`iter_routes` as an aligned three-column table."""
    rows = iter_routes(router, prefix=prefix)
    if not rows:
        return "(no routes registered)"

    def method_col(r: RouteInfo) -> str:
        if r.kind == "mount":
            return "MOUNT"
        return ",".join(r.methods) if r.methods else "-"

    left = [method_col(r) for r in rows]
    mid = [r.path for r in rows]
    lw = max(len(s) for s in left)
    mw = max(len(s) for s in mid)

    lines = []
    for r, lcol, mcol in zip(rows, left, mid):
        tail = r.name and f"  ({r.name})" or ""
        lines.append(f"{lcol:<{lw}}  {mcol:<{mw}}  {r.endpoint}{tail}")
    return "\n".join(lines)


def print_routes(router: Any, *, file: IO[str] | None = None) -> None:
    """Print :func:`format_routes` to ``file`` (stdout by default)."""
    print(format_routes(router), file=file or sys.stdout)
