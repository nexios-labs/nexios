"""
sillo.security.ratelimit._middleware — the rate-limit middleware.

Wires a :class:`RateLimitConfig` to a resolved strategy + backend, evaluates
each request, and either lets it through (attaching ``X-RateLimit-*`` headers)
or short-circuits with a ``429`` response carrying ``Retry-After``.
"""

from __future__ import annotations

from typing import Any

from sillo.core.http import HttpContext
from sillo.middleware.response_headers import ResponseHeaders
from sillo.responses import json
from sillo.types import ASGIApp, Message, Receive, Scope, Send

from .backends import RateLimitBackend, get_backend
from .config import RateLimitConfig
from .strategies import RateLimitStrategy, get_strategy

_HEADER_LIMIT = "X-RateLimit-Limit"
_HEADER_REMAINING = "X-RateLimit-Remaining"
_HEADER_RESET = "X-RateLimit-Reset"


class RateLimitMiddleware:
    """Enforce request rate limits per client identity."""

    def __init__(
        self,
        config: RateLimitConfig | None = None,
        **kwargs: Any,
    ) -> None:
        """Init"""
        # Bound on afterwards by `use()`: this is registered as a configured
        # instance, `app.use(RateLimitMiddleware(config))`.
        self.app: ASGIApp | None = None

        if config is not None and not isinstance(config, RateLimitConfig):
            raise TypeError("config must be a RateLimitConfig instance")
        self.config: RateLimitConfig = config or RateLimitConfig()
        self._strategy: RateLimitStrategy = get_strategy(self.config.strategy)
        self._backend: RateLimitBackend = get_backend(self.config.backend)

    def _inner(self) -> ASGIApp:
        """Return the inner application, refusing to serve without one."""
        if self.app is None:
            raise RuntimeError(
                "RateLimitMiddleware was constructed without an inner "
                "application and cannot serve requests. Register it with "
                "app.use(RateLimitMiddleware(...))."
            )
        return self.app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Count the hit, deny or continue, then stamp the limit headers."""
        app = self._inner()
        if scope["type"] != "http":
            await app(scope, receive, send)
            return

        ctx = HttpContext(scope, receive)
        result = await self.check(ctx)

        if result is not None and not result.allowed:
            response = self._deny(ctx, result)
            await response(scope, receive, send)
            return

        async def send_with_limit_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                self.set_limit_headers(ResponseHeaders(message), result)
            await send(message)

        await app(scope, receive, send_with_limit_headers)

    async def check(self, ctx: HttpContext) -> Any | None:
        """Count this request against its client's limit.

        Returns the strategy's result, or `None` when there was nothing to
        count (no key, or the backend failed open) -- the caller reads
        `result.allowed` to decide whether to deny it.
        """
        key = self.config._key_func(ctx)
        if key is None:
            return None

        full_key = f"{self.config.namespace}:{key}"
        try:
            return await self._strategy.hit(
                self._backend,
                full_key,
                self.config.limit,
                self.config.window,
                cost=self.config.cost,
            )
        except Exception:
            if not self.config.fail_open:
                raise
            # Backend unavailable -> allow, but don't attach limit headers.
            return None

    def set_limit_headers(self, headers: ResponseHeaders, result: Any | None) -> None:
        """Write the ``X-RateLimit-*`` headers onto the outgoing response."""
        if result is None or not self.config.include_headers:
            return
        headers.set_header(_HEADER_LIMIT, str(result.limit), override=True)
        headers.set_header(_HEADER_REMAINING, str(result.remaining), override=True)
        headers.set_header(_HEADER_RESET, str(int(result.reset_at)), override=True)

    def _deny(self, ctx: HttpContext, result: Any):
        """Build the 429, or hand off to a configured ``on_exceed``."""
        if callable(self.config.on_exceed):
            return self.config.on_exceed(ctx, result)  # ty: ignore[call-top-callable]
        retry_after = max(int(result.retry_after), 1)
        return json(
            {
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Slow down and retry later.",
                "retry_after": retry_after,
            },
            status_code=429,
            headers={
                _HEADER_LIMIT: str(result.limit),
                _HEADER_REMAINING: "0",
                _HEADER_RESET: str(int(result.reset_at)),
                "Retry-After": str(retry_after),
            },
        )
