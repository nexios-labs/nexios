from __future__ import annotations

import re
from base64 import b64encode
from collections.abc import Iterable, Mapping
from hashlib import sha1
from typing import Any, Protocol

from sillo.core.http import HttpContext
from sillo.core.http.response import BaseResponse
from sillo.middleware.response_headers import ResponseHeaders
from sillo.types import ASGIApp, Message, Receive, Scope, Send

_WEAK_PREFIX = "W/"
_ETAG_TOKEN_RE = re.compile(r'^(W/)?\s*"[^"]*"\s*$')


class _HasHeaders(Protocol):
    """What these functions actually need: a header-editing surface.

    A :class:`BaseResponse` satisfies this, and so does a
    :class:`~sillo.middleware.response_headers.ResponseHeaders` -- the
    editor `ETagMiddleware` hands these functions when it has buffered a
    response rather than built one. Neither is named here so this stays
    correct if a third kind of header-editable object ever needs an ETag
    stamped on it.
    """

    @property
    def headers(self) -> Mapping[str, str]: ...

    def set_header(self, key: str, value: str, override: bool = ...) -> Any: ...


def generate_etag_from_bytes(data: bytes, weak: bool = True) -> str:
    h = sha1()
    h.update(data)
    tag = f'"{b64encode(h.digest()).decode("utf-8")}"'
    return f"{_WEAK_PREFIX}{tag}" if weak else tag


def normalize_etag(tag: str) -> str:
    tag = tag.strip()
    if not _ETAG_TOKEN_RE.match(tag):
        if not tag.startswith(_WEAK_PREFIX):
            tag = f'"{tag.strip(chr(34))}"'
        else:
            tag = f'{_WEAK_PREFIX}"{tag[2:].strip().strip(chr(34))}"'
    if not _ETAG_TOKEN_RE.match(tag):
        raise ValueError(f"Invalid ETag token: {tag}")
    return tag


def set_response_etag(response: _HasHeaders, etag: str, override: bool = True) -> None:
    response.set_header("etag", normalize_etag(etag), override=override)


def compute_and_set_etag(
    response: _HasHeaders, body: bytes = b"", weak: bool = True, override: bool = False
) -> str:
    tag = generate_etag_from_bytes(body, weak=weak)
    set_response_etag(response, tag, override=override)
    return tag


def parse_if_none_match(ctx: HttpContext) -> list[str]:
    return _parse_etag_list(ctx.headers.get("if-none-match"))


def parse_if_match(ctx: HttpContext) -> list[str]:
    return _parse_etag_list(ctx.headers.get("if-match"))


def _parse_etag_list(value: str | None) -> list[str]:
    if not value:
        return []
    tags: list[str] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            tags.append(normalize_etag(part))
        except ValueError:
            continue
    return tags


def etag_matches(
    etag: str, candidates: Iterable[str], weak_compare: bool = True
) -> bool:
    try:
        normalized = normalize_etag(etag)
    except ValueError:
        return False

    def strip_weak(value: str) -> str:
        return value[2:] if value.startswith(_WEAK_PREFIX) else value

    for candidate in candidates:
        try:
            normalized_candidate = normalize_etag(candidate)
        except ValueError:
            continue
        if weak_compare:
            if strip_weak(normalized_candidate) == strip_weak(normalized):
                return True
        elif normalized_candidate == normalized:
            return True
    return False


def is_fresh(
    ctx: HttpContext, response: _HasHeaders, weak_compare: bool = True
) -> bool:
    current = response.headers.get("etag")
    if not current:
        return False
    return etag_matches(current, parse_if_none_match(ctx), weak_compare=weak_compare)


class ETagMiddleware:
    """Compute ETag headers and handle ``If-None-Match`` conditionals.

    An ETag has to be computed from the actual response body, and there is
    no telling whether the downstream app is done writing that body until it
    sends a final ``http.response.body`` message with ``more_body`` unset --
    so unlike the header-only middleware in this package, this one has to
    fully buffer a matching response before it can decide what to send:
    a 304 with no body at all, or the original response with an ``ETag``
    header added. Nothing here needs a body it isn't already going to send,
    so nothing is held any longer than it takes to make that one decision.
    """

    def __init__(
        self,
        *,
        weak: bool = True,
        methods: Iterable[str] = ("GET", "HEAD"),
        override: bool = False,
        **kwargs: Any,
    ) -> None:
        # Bound on afterwards by `use()`: this is registered as a configured
        # instance, `app.use(ETagMiddleware(...))`.
        self.app: ASGIApp | None = None
        self.weak = weak
        self.methods = tuple(method.upper() for method in methods)
        self.override = override

    def _inner(self) -> ASGIApp:
        """Return the inner application, refusing to serve without one."""
        if self.app is None:
            raise RuntimeError(
                "ETagMiddleware was constructed without an inner application "
                "and cannot serve requests. Register it with "
                "app.use(ETagMiddleware(...))."
            )
        return self.app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Buffer a matching response, then attach an ETag or answer 304."""
        app = self._inner()
        if scope["type"] != "http" or scope["method"].upper() not in self.methods:
            await app(scope, receive, send)
            return

        ctx = HttpContext(scope, receive)
        start_message: Message | None = None
        body = bytearray()

        async def buffer(message: Message) -> None:
            nonlocal start_message
            if message["type"] == "http.response.start":
                start_message = message
            elif message["type"] == "http.response.body":
                body.extend(message.get("body", b""))

        await app(scope, receive, buffer)

        assert start_message is not None, "downstream app sent no response.start"
        await self.finish(ctx, start_message, bytes(body), send)

    async def finish(
        self,
        ctx: HttpContext,
        start_message: Message,
        body: bytes,
        send: Send,
    ) -> None:
        """Decide the ETag, then send either the buffered response or a 304."""
        headers = ResponseHeaders(start_message)

        has_existing = bool(headers.headers.get("etag"))
        if not has_existing or self.override:
            compute_and_set_etag(headers, body, weak=self.weak, override=True)

        if is_fresh(ctx, headers, weak_compare=True):
            not_modified_headers = [
                (name, value)
                for name, value in start_message["headers"]
                if name.decode("latin-1").lower() in _NOT_MODIFIED_HEADERS
            ]
            await send(
                {
                    "type": "http.response.start",
                    "status": 304,
                    "headers": not_modified_headers,
                }
            )
            await send({"type": "http.response.body", "body": b""})
            return

        await send(start_message)
        await send({"type": "http.response.body", "body": body})


#: Headers RFC 9110 §15.4.5 requires a 304 to carry when the corresponding
#: 200 would have carried them. Everything else is dropped: a 304 says "your
#: copy is current", so describing a body that is not being sent is noise at
#: best and contradictory at worst.
_NOT_MODIFIED_HEADERS = (
    "etag",
    "cache-control",
    "content-location",
    "date",
    "expires",
    "vary",
)


def _response_body(response: BaseResponse) -> bytes | None:
    try:
        body = response.body
    except AttributeError:
        return None
    if isinstance(body, bytes):
        return body
    if isinstance(body, memoryview):
        return bytes(body)
    if isinstance(body, str):
        return body.encode("utf-8")
    return None


def ETag(
    weak: bool = True, methods: Iterable[str] = ("GET", "HEAD"), override: bool = False
) -> ETagMiddleware:
    return ETagMiddleware(weak=weak, methods=methods, override=override)


__all__ = [
    "ETag",
    "ETagMiddleware",
    "compute_and_set_etag",
    "etag_matches",
    "generate_etag_from_bytes",
    "is_fresh",
    "normalize_etag",
    "parse_if_match",
    "parse_if_none_match",
    "set_response_etag",
]
