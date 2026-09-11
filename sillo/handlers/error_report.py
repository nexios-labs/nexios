"""The block Sillo logs when a request raises and nothing handled it.

A Python traceback is a transcript — every frame, framework and stdlib and
your code weighted the same. This keeps only the frames in *your* code and
lays them out as log lines you can read at a glance: what broke, then each of
your frames as ``file:line  in function`` with the line itself under it, the
raising line marked.

    💥 oops — ValueError: seat 12A on flight BA2490 is already taken
        request   POST /flights/BA2490/book
        at        routes/flights.py:9   in book_seat
                  → await reserve_seat(code, "12A")
        at        booking/service.py:12   in reserve_seat
                › raise ValueError(f"seat {label} on flight {flight} is already taken")
        with      flight='BA2490', label='12A', hold_token=***, passenger=<dict len=2>
        from      KeyError: '12A'   at booking/service.py:5

The ``file:line`` is coloured (cyan, the line number bright), the function
name bold; ``with`` lists the raising frame's own locals — scalars and small
containers verbatim, a big one as ``<dict len=N>``, anything whose name reads
like a secret as ``***``.

`SILLO_TRACE` sets the depth: ``off`` logs nothing here (the 500's own log
line still stands), ``app`` (the default while ``debug`` is on) logs the
block, ``full`` appends the raw traceback under it. Off a terminal, or with
``debug`` off, the block is skipped and one structured line is logged
instead — what a log shipper wants.
"""

from __future__ import annotations

import os
import site
import sys
import sysconfig
import traceback
import typing

from sillo.console.style import DANGER, INFO, MUTED, PRIMARY, Palette, Style

if typing.TYPE_CHECKING:
    from sillo.core.http import HttpContext

EMOJI = "💥"
WORD = "oops"
THROW = "›"
CALL = "→"

_MODES = ("off", "app", "full")
_BOLD = Style(bold=True)
_LOC = INFO  # file paths and line numbers: a readable location colour
_LOC_N = INFO | Style(bold=True)  # the line number itself

#: Local names whose value is never printed, however it is spelled.
_SECRET = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "auth",
    "cookie",
    "session",
    "credential",
    "private_key",
    "signature",
)
_STDLIB = os.path.realpath(sysconfig.get_paths()["stdlib"])
try:
    _SITE = tuple(
        os.path.realpath(p)
        for p in (*site.getsitepackages(), site.getusersitepackages())
    )
except AttributeError:  # a virtualenv without getsitepackages
    _SITE = ()


def _app_root() -> str:
    """Where the project's own code lives — ``SILLO_APP_ROOT`` or the cwd.

    Read fresh each call: the process may ``chdir`` after import, and a test
    needs to point it elsewhere.
    """
    return os.path.realpath(os.environ.get("SILLO_APP_ROOT", os.getcwd()))


def trace_mode(debug: bool) -> str:
    """Resolve ``SILLO_TRACE``: an explicit value, else follow ``debug``."""
    raw = os.environ.get("SILLO_TRACE", "").strip().lower()
    if raw in _MODES:
        return raw
    return "app" if debug else "off"


def _is_app_frame(filename: str) -> bool:
    """Whether a frame is the project's own code, not a dependency."""
    path = os.path.realpath(filename)
    if path.startswith(_STDLIB) or any(path.startswith(p) for p in _SITE):
        return False
    if f"{os.sep}sillo{os.sep}" in path:
        return False
    return path.startswith(_app_root())


def _short(filename: str) -> str:
    """A frame's path, relative to the project root when it is under it."""
    path = os.path.realpath(filename)
    root = _app_root()
    if path.startswith(root):
        return os.path.relpath(path, root)
    return os.path.basename(path)


def _line_at(filename: str, lineno: int) -> str:
    """The statement at ``lineno``, trimmed to one line.

    A statement split across lines — ``raise ValueError(\\n  "msg"\\n)`` — is
    reassembled by reading on while brackets are unbalanced, up to two extra
    lines, so the marked line is not just ``raise ValueError(``.
    """
    try:
        with open(filename, encoding="utf-8", errors="replace") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return ""
    if not 1 <= lineno <= len(lines):
        return ""
    parts = [lines[lineno - 1]]
    depth = _bracket_depth(parts[0])
    extra = lineno
    while depth > 0 and extra < len(lines) and extra - lineno < 2:
        parts.append(lines[extra])
        depth += _bracket_depth(lines[extra])
        extra += 1
    text = " ".join(p.strip() for p in parts).expandtabs(4)
    return text if len(text) <= 100 else text[:99] + "…"


def _bracket_depth(text: str) -> int:
    depth = 0
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
    return depth


def _clip(text: str, width: int = 100) -> str:
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "…"


def _app_frames(exc: BaseException) -> list[traceback.FrameSummary]:
    return [
        fs
        for fs in traceback.extract_tb(exc.__traceback__)
        if _is_app_frame(fs.filename)
    ]


def _cause(exc: BaseException) -> BaseException | None:
    if exc.__cause__ is not None:
        return exc.__cause__
    if exc.__context__ is not None and not exc.__suppress_context__:
        return exc.__context__
    return None


def _deepest_app_frame(exc: BaseException):
    """The live frame object for the deepest frame in the project's code.

    ``traceback.extract_tb`` throws the frames away, and locals live on the
    frame — so the traceback list is walked here directly.
    """
    tb = exc.__traceback__
    found = None
    while tb is not None:
        if _is_app_frame(tb.tb_frame.f_code.co_filename):
            found = tb.tb_frame
        tb = tb.tb_next
    return found


def _short_repr(value: object) -> str:
    """A one-glance value.

    Scalars and small containers as their own ``repr``; a big container as
    ``<dict len=42>``; anything else as ``<ClassName>``.
    """
    if isinstance(value, (str, bytes, int, float, bool)) or value is None:
        text = repr(value)
        return text if len(text) <= 48 else text[:47] + "…"
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        text = repr(value)
        return text if len(text) <= 48 else f"<{type(value).__name__} len={len(value)}>"
    name = type(value).__name__
    sized = getattr(value, "__len__", None)
    if callable(sized):
        try:
            return f"<{name} len={sized()}>"
        except Exception:
            pass
    return f"<{name}>"


def _locals_line(frame) -> str:
    """A ``name=value`` summary of a frame's own locals — redacted, capped.

    Only the simple, immediately useful names: no ``self`` / ``cls``, no
    dunders, no imported modules, and anything whose name reads like a secret
    is shown as ``***``.
    """
    if frame is None:
        return ""
    pairs: list[str] = []
    for name, value in frame.f_locals.items():
        if name in ("self", "cls") or name.startswith("__"):
            continue
        if type(value).__name__ == "module":
            continue
        if any(s in name.lower() for s in _SECRET):
            pairs.append(f"{name}=***")
        else:
            pairs.append(f"{name}={_short_repr(value)}")
        if len(pairs) == 6:
            break
    return ", ".join(pairs)


def render(
    exc: BaseException,
    ctx: HttpContext | None = None,
    *,
    palette: Palette | None = None,
    mode: str = "app",
) -> str:
    """Build the block for ``exc``.

    ``mode`` is ``app`` (the block) or ``full`` (the block then the raw
    traceback). A disabled ``palette`` returns plain text.
    """
    p = palette or Palette()

    def c(text: str, style: Style) -> str:
        return p.render(text, style)

    def label(word: str) -> str:
        # Pad before colouring: ANSI codes have no display width.
        return "    " + c(word.ljust(10), MUTED)

    out: list[str] = []

    # -- what broke --------------------------------------------------
    message = _clip(str(exc)) or "(no message)"
    out.append(
        f"{EMOJI} {c(WORD, PRIMARY)} — "
        f"{c(type(exc).__name__, DANGER | _BOLD)}: {message}"
    )

    if ctx is not None:
        method = getattr(ctx, "method", "?")
        path = getattr(getattr(ctx, "url", None), "path", "") or ctx.scope.get(
            "path", "?"
        )
        out.append(f"{label('request')}{method} {path}")

    # -- your frames, outermost first -----------------------------
    frames = _app_frames(exc)
    if not frames:
        # The error is entirely inside a dependency; still show where.
        tail = traceback.extract_tb(exc.__traceback__)
        if tail:
            frames = [tail[-1]]
    for i, fs in enumerate(frames):
        last = i == len(frames) - 1
        where = (
            f"{c(_short(fs.filename), _LOC)}{c(':', _LOC)}{c(str(fs.lineno), _LOC_N)}"
        )
        out.append(f"{label('at')}{where}   in {c(fs.name, _BOLD)}")
        src = _line_at(fs.filename, fs.lineno or 0)
        if src:
            if last:
                out.append(f"            {c(THROW, PRIMARY)} {src}")
            else:
                out.append(f"              {c(CALL, MUTED)} {c(src, MUTED)}")
        if last:
            values = _locals_line(_deepest_app_frame(exc))
            if values:
                out.append(f"{label('with')}{c(values, MUTED)}")

    # -- what it was raised from ---------------------------------
    cause = _cause(exc)
    if cause is not None:
        at = ""
        c_frames = _app_frames(cause) or traceback.extract_tb(cause.__traceback__)
        if c_frames:
            f = c_frames[-1]
            at = (
                f"   at {c(_short(f.filename), _LOC)}"
                f"{c(':', _LOC)}{c(str(f.lineno), _LOC_N)}"
            )
        out.append(
            f"{label('from')}{type(cause).__name__}: {_clip(str(cause), 70)}{at}"
        )

    if mode == "full":
        out.append("")
        out.append(
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        )

    return "\n".join(out)


def one_line(exc: BaseException, ctx: HttpContext | None) -> str:
    """The single structured line for a non-terminal sink — no colour, no block."""
    frames = _app_frames(exc)
    at = f" at={_short(frames[-1].filename)}:{frames[-1].lineno}" if frames else ""
    where = ""
    if ctx is not None:
        path = getattr(getattr(ctx, "url", None), "path", "") or ctx.scope.get(
            "path", "?"
        )
        where = f" {getattr(ctx, 'method', '?')} {path}"
    return f"500{where} {type(exc).__name__}: {_clip(str(exc), 120)}{at}"


def emit(exc: BaseException, ctx: HttpContext | None, *, debug: bool) -> str:
    """Write the block to the terminal, return the one-line summary to log.

    The block goes straight to ``stderr`` — the logger's ``[time] LEVEL in
    module:`` prefix would fight the layout. When ``stderr`` is not a
    terminal, or ``SILLO_TRACE`` is ``off``, nothing is written and the
    returned line is logged instead.
    """
    mode = trace_mode(debug)
    at_terminal = bool(getattr(sys.stderr, "isatty", lambda: False)())
    if mode != "off" and at_terminal:
        sys.stderr.write(
            render(exc, ctx, palette=Palette(sys.stderr), mode=mode) + "\n"
        )
        sys.stderr.flush()
    return one_line(exc, ctx)
