"""The block Sillo prints when a request raises and nothing handled it.

A Python traceback is a transcript: every frame, deepest last, framework and
stdlib and your code given equal weight. Reading it is work. This renders the
same failure the way you would summarise it to someone: what broke, the one
line of *your* code it broke on, the path the request took to get there, and an
id to grep for — inside a brand gutter so it stands out of the request stream
without a box swallowing the terminal.

    ▍ ops · ValueError
    ▍ seat 12A on flight BA2490 is already taken
    ▍
    ▍ app/booking/service.py:88  in reserve_seat
    ▍    87    if seat.taken:
    ▍  › 88        raise ValueError(f"seat {label} ...")
    ▍    89    seat.taken = True
    ▍
    ▍ route  POST /flights/BA2490/book → book_seat → reserve_seat  · +7 framework
    ▍ caused by  KeyError: 'seat_map'  at service.py:72
    ▍ err_7f3a91 · 20:14:07 · full trace → SILLO_TRACE=full

`SILLO_TRACE` decides the depth: ``off`` prints nothing here (the access-log
line for the 500 still stands), ``app`` (the default while ``debug`` is on)
prints the block, ``full`` appends the raw traceback under it. Off a TTY, or
with ``debug`` off, none of this renders — a single structured line goes to the
logger instead, which is what a log shipper wants.
"""

from __future__ import annotations

import hashlib
import os
import site
import sys
import sysconfig
import time
import traceback
import typing

from sillo.console.style import DANGER, MUTED, PRIMARY, WARNING, Palette, Style

if typing.TYPE_CHECKING:
    from sillo.core.http import HttpContext

BAR = "▍"
MARK = "›"
LABEL = "ops"

#: How the block is rendered. Set from ``SILLO_TRACE`` at call time so a test
#: or a running process can change it without a restart.
_MODES = ("off", "app", "full")

_HANDLER = Style(bold=True)
_STDLIB = os.path.realpath(sysconfig.get_paths()["stdlib"])
try:
    _SITE = tuple(
        os.path.realpath(p)
        for p in (*site.getsitepackages(), site.getusersitepackages())
    )
except AttributeError:  # a virtualenv without getsitepackages
    _SITE = ()


def _app_root() -> str:
    """Where the project's own code lives.

    ``SILLO_APP_ROOT`` when set, otherwise the working directory. Read fresh
    each call rather than frozen at import: the process may ``chdir`` after
    import, and a test needs to point it somewhere else.
    """
    return os.path.realpath(os.environ.get("SILLO_APP_ROOT", os.getcwd()))


def trace_mode(debug: bool) -> str:
    """Resolve the effective ``SILLO_TRACE`` level.

    Unset, it follows ``debug``: the block while developing, silence in
    production. An explicit value always wins.
    """
    raw = os.environ.get("SILLO_TRACE", "").strip().lower()
    if raw in _MODES:
        return raw
    return "app" if debug else "off"


def _is_app_frame(filename: str) -> bool:
    """Whether a frame belongs to the project rather than a dependency.

    Project code lives under the working directory (or ``SILLO_APP_ROOT``);
    the stdlib, installed packages and sillo itself do not count, even when a
    checkout of one happens to sit under the same root.
    """
    path = os.path.realpath(filename)
    if path.startswith(_STDLIB) or any(path.startswith(p) for p in _SITE):
        return False
    if f"{os.sep}sillo{os.sep}" in path:
        return False
    return path.startswith(_app_root())


def _short(filename: str) -> str:
    """A frame's path, made relative to the project root when it is under it."""
    path = os.path.realpath(filename)
    root = _app_root()
    if path.startswith(root):
        return os.path.relpath(path, root)
    return os.path.basename(path)


def _module_of(filename: str) -> str:
    """A dependency frame's top package name, for the ``+N framework`` tally."""
    path = os.path.realpath(filename)
    for root in _SITE:
        if path.startswith(root):
            rest = path[len(root) :].lstrip(os.sep)
            return rest.split(os.sep, 1)[0].removesuffix(".py")
    if f"{os.sep}sillo{os.sep}" in path:
        return "sillo"
    if path.startswith(_STDLIB):
        return os.path.basename(path).removesuffix(".py")
    return "?"


def _clip(text: str, width: int = 96) -> str:
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "…"


def _source(filename: str, lineno: int, radius: int = 1) -> list[tuple[int, str]]:
    """A few real source lines around ``lineno``, or nothing if unreadable."""
    try:
        with open(filename, encoding="utf-8", errors="replace") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return []
    lo = max(1, lineno - radius)
    hi = min(len(lines), lineno + radius)
    return [(n, lines[n - 1]) for n in range(lo, hi + 1)]


def error_id(exc: BaseException) -> str:
    """A short, stable id for this failure's *signature*.

    The exception type plus the deepest app frame — so the same bug lands on
    the same id across requests and restarts, and the id in the log matches the
    one on the response.
    """
    tb = exc.__traceback__
    site_key = ""
    while tb is not None:
        f = tb.tb_frame
        if _is_app_frame(f.f_code.co_filename):
            site_key = f"{f.f_code.co_filename}:{tb.tb_lineno}"
        tb = tb.tb_next
    digest = hashlib.sha1(
        f"{type(exc).__name__}:{site_key or exc}".encode()
    ).hexdigest()
    return digest[:6]


def _app_frames(exc: BaseException) -> list[traceback.FrameSummary]:
    return [
        fs
        for fs in traceback.extract_tb(exc.__traceback__)
        if _is_app_frame(fs.filename)
    ]


def _framework_tally(exc: BaseException) -> tuple[int, list[str]]:
    seen: list[str] = []
    count = 0
    for fs in traceback.extract_tb(exc.__traceback__):
        if _is_app_frame(fs.filename):
            continue
        count += 1
        mod = _module_of(fs.filename)
        if mod not in seen and mod != "?":
            seen.append(mod)
    return count, seen[:3]


def render(
    exc: BaseException,
    ctx: HttpContext | None = None,
    *,
    palette: Palette | None = None,
    mode: str = "app",
) -> str:
    """Build the block for ``exc``.

    ``mode`` is one of ``app`` (the block) or ``full`` (the block plus the raw
    traceback). ``palette`` colours it; a disabled palette returns plain text,
    which is what a file or a pipe should get.
    """
    p = palette or Palette()

    def paint(text: str, style: Style) -> str:
        return p.render(text, style)

    bar = paint(BAR, PRIMARY)
    out: list[str] = [""]

    def row(text: str = "") -> None:
        out.append(f"{bar} {text}".rstrip())

    # -- what broke ----------------------------------------------------
    row(f"{paint(LABEL, PRIMARY)} · {paint(type(exc).__name__, DANGER | _HANDLER)}")
    message = _clip(str(exc)) or paint("(no message)", MUTED)
    row(message)

    # -- the line of your code it broke on ---------------------------
    app = _app_frames(exc)
    if app:
        deepest = app[-1]
        where = f"{_short(deepest.filename)}:{deepest.lineno}"
        row()
        row(f"{where}  {paint(f'in {deepest.name}', MUTED)}")
        block_lines = _source(deepest.filename, deepest.lineno or 0)
        # Re-indent the snippet against its own shallowest line so a nested
        # statement does not push off the right edge, but relative structure
        # is kept.
        common = min(
            (len(t) - len(t.lstrip()) for _, t in block_lines if t.strip()),
            default=0,
        )
        for n, text in block_lines:
            code = text[common:].rstrip().expandtabs(4)
            if len(code) > 84:
                code = code[:83] + "…"
            hit = n == deepest.lineno
            gutter = (
                paint(f"{MARK} {n:>3}", PRIMARY) if hit else paint(f"  {n:>3}", MUTED)
            )
            row(f"  {gutter}  {code if hit else paint(code, MUTED)}")

    # -- how the request got there ----------------------------------
    row()
    steps = " → ".join(fs.name for fs in app) if app else "—"
    count, mods = _framework_tally(exc)
    if count:
        named = f" ({', '.join(mods)})" if mods else ""
        tail = f"  · {paint(f'+{count} framework{named}', MUTED)}"
    else:
        tail = ""
    if ctx is not None:
        verb = getattr(ctx, "method", "?")
        path = getattr(getattr(ctx, "url", None), "path", "") or ctx.scope.get(
            "path", "?"
        )
        row(f"{paint('route', MUTED)}  {verb} {path} → {steps}{tail}")
    else:
        row(f"{paint('path', MUTED)}  {steps}{tail}")

    # -- the cause it was raised from -------------------------------
    cause = exc.__cause__ or (exc.__context__ if not exc.__suppress_context__ else None)
    if cause is not None:
        c_at = ""
        c_frames = _app_frames(cause) or traceback.extract_tb(cause.__traceback__)
        if c_frames:
            last = c_frames[-1]
            c_at = f"  {paint(f'at {os.path.basename(last.filename)}:{last.lineno}', MUTED)}"
        row(
            f"{paint('caused by', WARNING)}  "
            f"{type(cause).__name__}: {_clip(str(cause), 60)}{c_at}"
        )

    # -- the footer ------------------------------------------------
    eid = error_id(exc)
    when = time.strftime("%H:%M:%S")
    hint = "full trace → SILLO_TRACE=full" if mode != "full" else "raw trace below"
    row(paint(f"err_{eid} · {when} · {hint}", MUTED))
    out.append("")

    if mode == "full":
        out.append(
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        )

    return "\n".join(out)


def one_line(exc: BaseException, ctx: HttpContext | None) -> str:
    """The single structured line for a log shipper — no colour, no block.

    What a non-TTY sink (a file, journald, Loki) gets: greppable, one record,
    the same ``err_`` id the block and the response carry.
    """
    app = _app_frames(exc)
    at = ""
    if app:
        at = f" at={_short(app[-1].filename)}:{app[-1].lineno}"
    where = ""
    if ctx is not None:
        path = getattr(getattr(ctx, "url", None), "path", "") or ctx.scope.get(
            "path", "?"
        )
        where = f" {getattr(ctx, 'method', '?')} {path}"
    return (
        f"500{where} {type(exc).__name__}: {_clip(str(exc), 120)} "
        f"err_id={error_id(exc)}{at}"
    )


def emit(exc: BaseException, ctx: HttpContext | None, *, debug: bool) -> str:
    """Render the failure to the terminal and hand back the one-line summary.

    The block goes straight to ``stderr`` — wrapping it in the logger's
    ``[time] LEVEL in module:`` prefix would fight the layout, and it is a
    thing to read, not a record to ship. When ``stderr`` is not a terminal, or
    ``SILLO_TRACE`` is ``off``, nothing is written here; the returned string is
    logged instead so the sink still sees the 500.
    """
    mode = trace_mode(debug)
    at_terminal = bool(getattr(sys.stderr, "isatty", lambda: False)())
    if mode != "off" and at_terminal:
        block = render(exc, ctx, palette=Palette(sys.stderr), mode=mode)
        sys.stderr.write(block + "\n")
        sys.stderr.flush()
    return one_line(exc, ctx)
