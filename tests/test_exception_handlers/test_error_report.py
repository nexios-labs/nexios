"""The rendered error block — `sillo.handlers.error_report`.

Assertions read the plain (colour-disabled) render, the same text a log file
would carry.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from sillo import HttpContext, SilloApp
from sillo.console.style import Palette
from sillo.handlers import error_report
from sillo.testclient import TestClient

PLAIN = Palette(enabled=False)


def _raise(fn):
    try:
        fn()
    except Exception as exc:
        return exc
    raise AssertionError("fn did not raise")


def _ctx(method: str, path: str) -> SimpleNamespace:
    return SimpleNamespace(
        method=method, scope={"path": path}, url=SimpleNamespace(path=path)
    )


# ── trace_mode ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "env,debug,expected",
    [
        (None, True, "app"),
        (None, False, "off"),
        ("off", True, "off"),
        ("full", False, "full"),
        ("nonsense", True, "app"),
    ],
)
def test_trace_mode_follows_env_then_debug(monkeypatch, env, debug, expected):
    if env is None:
        monkeypatch.delenv("SILLO_TRACE", raising=False)
    else:
        monkeypatch.setenv("SILLO_TRACE", env)
    assert error_report.trace_mode(debug) == expected


# ── the block ───────────────────────────────────────────────────────────


def test_first_line_is_emoji_word_type_and_message():
    exc = _raise(lambda: (_ for _ in ()).throw(ValueError("seat 12A is taken")))
    first = error_report.render(exc, palette=PLAIN).splitlines()[0]
    assert first == "💥 oops — ValueError: seat 12A is taken"


def test_frames_show_file_line_function_and_the_line(tmp_path, monkeypatch):
    (tmp_path / "svc.py").write_text(
        "def outer():\n"
        "    inner()\n"
        "\n"
        "def inner():\n"
        "    value = 1\n"
        "    raise RuntimeError('nope')\n"
    )
    monkeypatch.setenv("SILLO_APP_ROOT", str(tmp_path))
    monkeypatch.syspath_prepend(str(tmp_path))
    import importlib

    svc = importlib.import_module("svc")
    block = error_report.render(_raise(svc.outer), palette=PLAIN)

    assert "at        svc.py:2   in outer" in block
    assert "→ inner()" in block
    assert "at        svc.py:6   in inner" in block
    assert "› raise RuntimeError('nope')" in block  # deepest frame, marked


def test_a_multiline_statement_is_reassembled(tmp_path, monkeypatch):
    (tmp_path / "m.py").write_text(
        "def boom():\n    raise ValueError(\n        'the seat is taken'\n    )\n"
    )
    monkeypatch.setenv("SILLO_APP_ROOT", str(tmp_path))
    monkeypatch.syspath_prepend(str(tmp_path))
    import importlib

    m = importlib.import_module("m")
    block = error_report.render(_raise(m.boom), palette=PLAIN)
    assert "› raise ValueError( 'the seat is taken' )" in block


def test_request_line_is_shown_when_a_context_is_given():
    block = error_report.render(
        _raise(lambda: 1 / 0), _ctx("POST", "/pay"), palette=PLAIN
    )
    assert "    request   POST /pay" in block


def test_no_request_line_without_a_context():
    block = error_report.render(_raise(lambda: 1 / 0), palette=PLAIN)
    assert "request" not in block


def test_chained_cause_is_one_line():
    def inner():
        try:
            {}["k"]
        except KeyError as missing:
            raise ValueError("wrapped") from missing

    block = error_report.render(_raise(inner), palette=PLAIN)
    from_lines = [ln for ln in block.splitlines() if ln.lstrip().startswith("from")]
    assert len(from_lines) == 1
    assert "KeyError: 'k'" in from_lines[0]


def test_no_error_id_or_footer():
    block = error_report.render(_raise(lambda: 1 / 0), _ctx("GET", "/x"), palette=PLAIN)
    assert "err_" not in block
    assert "SILLO_TRACE" not in block


def test_full_mode_appends_the_raw_traceback():
    block = error_report.render(_raise(lambda: 1 / 0), palette=PLAIN, mode="full")
    assert "Traceback (most recent call last)" in block
    assert "ZeroDivisionError" in block


def test_an_error_wholly_inside_a_dependency_still_shows_a_frame():
    # json.loads raises entirely within the stdlib
    import json

    block = error_report.render(_raise(lambda: json.loads("{")), palette=PLAIN)
    assert "\n    at        " in block


# ── one_line / emit ─────────────────────────────────────────────────────


def test_one_line_is_greppable_and_has_no_id():
    exc = _raise(lambda: (_ for _ in ()).throw(ValueError("boom")))
    line = error_report.one_line(exc, _ctx("GET", "/x"))
    assert line.startswith("500 GET /x ValueError: boom")
    assert "err_" not in line and "\n" not in line


def test_emit_writes_nothing_to_a_non_terminal_but_returns_the_line(capsys):
    line = error_report.emit(_raise(lambda: 1 / 0), None, debug=True)
    assert line.startswith("500") and "ZeroDivisionError" in line
    assert capsys.readouterr().err == ""


def test_emit_respects_trace_off(monkeypatch, capsys):
    monkeypatch.setenv("SILLO_TRACE", "off")
    error_report.emit(_raise(lambda: 1 / 0), None, debug=True)
    assert capsys.readouterr().err == ""


# ── end to end ─────────────────────────────────────────────────────────


def test_a_500_logs_exactly_one_structured_line(caplog):
    app = SilloApp(debug=False)

    @app.get("/boom")
    async def boom(ctx: HttpContext):
        raise ValueError("kaboom")

    with caplog.at_level("ERROR", logger="sillo"):
        resp = TestClient(app).get("/boom")

    assert resp.status_code == 500
    hits = [r for r in caplog.records if "kaboom" in r.getMessage()]
    assert len(hits) == 1
    assert hits[0].getMessage().startswith("500 GET /boom ValueError: kaboom")
