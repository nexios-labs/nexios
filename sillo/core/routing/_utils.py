import re
from enum import Enum

from sillo.types import Scope

# Path convertors whose regex is narrower than the default string segment
# (`[^/]+`). A route that pins a segment to one of these is more specific
# than one that accepts any string there, so it should be tried first.
_TIGHT_CONVERTORS = frozenset({"int", "float", "uuid"})

_SEGMENT_PARAM = re.compile(r"\{([a-zA-Z_]\w*)(?::([^}]+))?\}")

# Per-segment specificity ranks. Lower is more specific.
_RANK_LITERAL = 0
_RANK_TIGHT_PARAM = 1
_RANK_STRING_PARAM = 2
_RANK_WILDCARD = 3


def _segment_rank(segment: str) -> int:
    """Rank one path segment by how tightly it constrains a match.

    ``0`` a literal segment (``users``), ``1`` a parameter pinned to a narrow
    convertor (``{id:int}``), ``2`` a plain string parameter (``{name}`` or
    ``{name:str}``), ``3`` a catch-all — the ``path`` convertor, a regex
    segment, or a segment that mixes a literal and a parameter.
    """
    if "{" not in segment:
        return _RANK_LITERAL
    match = _SEGMENT_PARAM.fullmatch(segment)
    if match is None:
        # `/v{n}` style or an unparseable regex segment — treat as loose.
        return _RANK_WILDCARD
    convertor = match.group(2)
    if convertor is None or convertor == "str":
        return _RANK_STRING_PARAM
    if convertor in _TIGHT_CONVERTORS:
        return _RANK_TIGHT_PARAM
    if convertor == "path" or "." in convertor or "*" in convertor:
        return _RANK_WILDCARD
    # Any other named convertor is still a single narrowed segment.
    return _RANK_TIGHT_PARAM


def route_specificity(
    raw_path: str, *, trailing_wildcard: bool = False
) -> tuple[int, ...]:
    """Build the match-ordering key for a route path.

    The key is the tuple of per-segment ranks, compared lexicographically, so
    a literal segment always beats a parameter at the same position and the
    leftmost segment that differs decides. ``/users/me`` (``(0, 0)``) therefore
    sorts ahead of ``/users/{id}`` (``(0, 2)``) no matter which was registered
    first. ``trailing_wildcard`` appends a catch-all rank, used for mounted
    sub-routers, which always consume an open-ended suffix.
    """
    ranks = [_segment_rank(s) for s in raw_path.strip("/").split("/") if s]
    if trailing_wildcard:
        ranks.append(_RANK_WILDCARD)
    return tuple(ranks)


def route_order_key(route: object) -> tuple:
    """Sort key that puts the most specific, highest-priority route first.

    ``priority`` (an explicit integer, default ``0``) dominates; within the
    same priority the specificity tuple decides; equal keys keep registration
    order because the sort is stable.
    """
    priority = getattr(route, "priority", 0)
    spec = getattr(route, "_specificity", None)
    if spec is None:
        trailing = type(route).__name__ == "Group"
        spec = route_specificity(
            getattr(route, "raw_path", ""), trailing_wildcard=trailing
        )
    return (-priority, spec)


class MatchStatus(Enum):
    """Enumeration for route matching status.

    This enum is used throughout the routing system to indicate the result
    of attempting to match an incoming request path against a route pattern.
    It provides three distinct states that allow the router to make informed
    decisions about how to dispatch requests.

    Attributes:
        NONE: Path does not match this route at all. The router should
            continue searching for other matching routes.
        PARTIAL: Path partially matches, more segments expected. The router
            may use this as a fallback if no full match is found.
        FULL: Path fully matches this route. The router should dispatch
            the request to this route's handler immediately.
    """

    NONE = 0
    PARTIAL = 1
    FULL = 2


def get_route_path(scope: Scope) -> str:
    """Extract the relative route path from an ASGI scope dictionary.

    Strips the root_path prefix from the full path to get the portion
    that should be used for route matching. This is essential for correctly
    routing requests when the application is mounted under a sub-path
    behind a reverse proxy or within another ASGI application.

    The function handles several edge cases including empty root paths,
    paths that exactly equal the root path, and paths that do not begin
    with the root path prefix.

    Args:
        scope: ASGI scope containing path and root_path keys. The path
            key holds the full request path while root_path holds the
            mount point of the application.

    Returns:
        The path relative to the mounted application root. If no root
        path is set or the path does not start with root_path, the
        original path is returned unchanged.

    Examples:
        >>> scope = {"path": "/api/users", "root_path": "/api"}
        >>> get_route_path(scope)
        '/users'
    """
    path: str = scope["path"]
    root_path = scope.get("root_path", "")
    if not root_path:
        return path

    if not path.startswith(root_path):
        return path

    if path == root_path:
        return ""

    return path.removeprefix(root_path)
