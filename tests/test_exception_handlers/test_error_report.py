"""The rendered error block — `sillo.handlers.error_report`.

Everything is checked against the plain (colour-disabled) render so the
assertions read the text the same way a log file would.
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


def _divide():
    return 1 / 0


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


def test_block_leads_with_the_exception_and_message():
    exc = _raise(lambda: (_ for _ in ()).throw(ValueError("seat 12A is taken")))
    block = error_report.render(exc, palette=PLAIN)

    lines = [ln for ln in block.splitlines() if ln.strip()]
    assert lines[0] == "▍ ops · ValueError"
    assert lines[1] == "▍ seat 12A is taken"


def test_block_points_at_the_app_frame_with_source_context(tmp_path, monkeypatch):
    mod = tmp_path / "svc.py"
    mod.write_text(
        "def boom():\n    x = 1\n    raise RuntimeError('nope')\n    return x\n"
    )
    monkeypatch.setenv("SILLO_APP_ROOT", str(tmp_path))
    monkeypatch.syspath_prepend(str(tmp_path))
    import importlib

    svc = importlib.import_module("svc")
    exc = _raise(svc.boom)

    block = error_report.render(exc, palette=PLAIN)
    assert "svc.py:3  in boom" in block
    assert "›   3" in block  # the marked line
    assert "raise RuntimeError('nope')" in block


def test_block_names_the_route_when_a_context_is_given():
    exc = _raise(lambda: 1 / 0)

    block = error_report.render(exc, _ctx("POST", "/pay"), palette=PLAIN)
    assert "route  POST /pay" in block


def test_block_surfaces_a_chained_cause():
    def inner():
        try:
            {}["k"]
        except KeyError as missing:
            raise ValueError("wrapped") from missing

    exc = _raise(inner)
    block = error_report.render(exc, palette=PLAIN)
    assert "caused by  KeyError" in block


def test_full_mode_appends_the_raw_traceback():
    exc = _raise(lambda: 1 / 0)
    block = error_report.render(exc, palette=PLAIN, mode="full")
    assert "raw trace below" in block
    assert "ZeroDivisionError" in block
    assert "Traceback (most recent call last)" in block


def test_error_id_is_stable_for_the_same_signature():
    a = _raise(_divide)
    b = _raise(_divide)
    assert error_report.error_id(a) == error_report.error_id(b)


def test_error_id_differs_by_exception_type():
    a = _raise(lambda: 1 / 0)
    b = _raise(lambda: (_ for _ in ()).throw(ValueError("x")))
    assert error_report.error_id(a) != error_report.error_id(b)


def test_one_line_is_greppable_and_carries_the_id():
    exc = _raise(lambda: (_ for _ in ()).throw(ValueError("boom")))

    line = error_report.one_line(exc, _ctx("GET", "/x"))
    assert line.startswith("500 GET /x ValueError: boom")
    assert f"err_id={error_report.error_id(exc)}" in line
    assert "\n" not in line


# ── emit() gating ──────────────────────────────────────────────────────


def test_emit_writes_nothing_to_a_non_terminal_but_returns_the_line(capsys):
    exc = _raise(lambda: 1 / 0)
    line = error_report.emit(exc, None, debug=True)
    assert "500" in line and "ZeroDivisionError" in line
    assert capsys.readouterr().err == ""  # capsys stderr is not a tty


def test_emit_respects_trace_off(monkeypatch, capsys):
    monkeypatch.setenv("SILLO_TRACE", "off")
    exc = _raise(lambda: 1 / 0)
    error_report.emit(exc, None, debug=True)
    assert capsys.readouterr().err == ""


# ── end to end through the middleware ─────────────────────────────────


def test_a_500_logs_exactly_one_structured_line(caplog):
    app = SilloApp(debug=False)

    @app.get("/boom")
    async def boom(ctx: HttpContext):
        raise ValueError("kaboom")

    with caplog.at_level("ERROR", logger="sillo"):
        resp = TestClient(app).get("/boom")

    assert resp.status_code == 500
    server_errors = [r for r in caplog.records if "kaboom" in r.getMessage()]
    assert len(server_errors) == 1
    assert server_errors[0].getMessage().startswith("500 GET /boom ValueError: kaboom")
