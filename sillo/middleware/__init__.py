"""Middleware: the contract applications write against, and the plumbing under it.

What is where:

``base``
    :class:`~sillo.middleware.base.BaseMiddleware` — the contract. Subclass it
    and override ``dispatch(ctx, call_next)``.
``define``
    :class:`~sillo.middleware.define.DefineMiddleware`, the deferred
    factory-plus-arguments pair the chain builders iterate, and
    :func:`~sillo.middleware.define.wrap_middleware`, which normalises a
    dispatch function into one.
``bridge``
    :class:`~sillo.middleware.bridge.ASGIRequestResponseBridge` — how a
    dispatch middleware is mounted above an ASGI application, which cannot
    return a response object on its own.
``gzip``, ``security``
    Middleware that ships with the framework. Every one of them -- here and
    under ``sillo.http`` (sessions, auth, CORS, CSRF, rate limiting, security
    headers, path normalization, request IDs, ETags, content negotiation) --
    is plain raw ASGI: ``__init__(self, app=None, ...)`` and
    ``async def __call__(self, scope, receive, send)``. None of them subclass
    ``BaseMiddleware`` or import it, so there is no cycle through ``base`` to
    worry about here any more.
``utils``
    :func:`~sillo.middleware.utils.use_for_route`, to scope a middleware to a
    path pattern.

Only ``base`` and the shipped middleware are public API. ``define`` and
``bridge`` are how the framework assembles a chain; import them by their
module path rather than from here.
"""

from sillo.security.cors import CORSMiddleware
from sillo.security.csrf import CSRFMiddleware

from .base import BaseMiddleware

__all__ = ["BaseMiddleware", "CORSMiddleware", "CSRFMiddleware"]
