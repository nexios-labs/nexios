from __future__ import annotations

from typing import Any

from sillo.core.http import HttpContext
from sillo.middleware.response_headers import ResponseHeaders
from sillo.types import ASGIApp, Message, Receive, Scope, Send

from .helpers import (
    generate_request_id,
    get_or_generate_request_id,
    get_request_id_from_header,
    set_request_id_header,
    store_request_id_in_request,
)


class RequestIdMiddleware:
    """Middleware that manages request ID generation and propagation.

    Automatically assigns a unique request ID to each incoming request,
    either by reading an existing ID from a configurable header or by
    generating a fresh UUID4. The ID is stored on the request state
    object and echoed back in the response header for client-side
    tracing and log correlation.

    Supports forced regeneration (ignoring client-supplied IDs),
    optional response header inclusion, and configurable attribute
    names for request state storage.
    """

    def __init__(
        self,
        *,
        header_name: str = "X-Request-ID",
        force_generate: bool = False,
        store_in_request: bool = True,
        request_attribute_name: str = "request_id",
        include_in_response: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the RequestIdMiddleware with tracing configuration.

        Configures how request IDs are sourced, stored, and propagated
        through the request/response pipeline. All parameters are
        keyword-only to prevent positional argument misuse.

        Args:
            header_name (str, optional): The HTTP header name used
                for reading and writing the request ID. Defaults to
                ``"X-Request-ID"``.
            force_generate (bool, optional): When ``True``, always
                generate a new UUID4 and ignore any client-supplied
                header value. Defaults to ``False``.
            store_in_request (bool, optional): When ``True``, persist
                the request ID on ``ctx.state`` for downstream
                access. Defaults to ``True``.
            request_attribute_name (str, optional): The attribute
                name used when storing the ID on ``ctx.state``.
                Defaults to ``"request_id"``.
            include_in_response (bool, optional): When ``True``, set
                the request ID as a header on the outgoing response.
                Defaults to ``True``.
            **kwargs: Additional keyword arguments, accepted but ignored,
                for compatibility with generic middleware configuration
                patterns.

        Returns:
            None.

        Raises:
            None.
        """
        # Bound on afterwards by `use()`: this is registered as a configured
        # instance, `app.use(RequestIdMiddleware(...))`.
        self.app: ASGIApp | None = None
        self.header_name = header_name
        self.force_generate = force_generate
        self.store_in_request = store_in_request
        self.request_attribute_name = request_attribute_name
        self.include_in_response = include_in_response

    def _inner(self) -> ASGIApp:
        """Return the inner application, refusing to serve without one."""
        if self.app is None:
            raise RuntimeError(
                "RequestIdMiddleware was constructed without an inner "
                "application and cannot serve requests. Register it with "
                "app.use(RequestIdMiddleware(...))."
            )
        return self.app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Assign a request ID, then guarantee it on the outgoing response."""
        app = self._inner()
        if scope["type"] != "http":
            await app(scope, receive, send)
            return

        ctx = HttpContext(scope, receive)
        request_id = self.assign_request_id(ctx)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                self.set_response_header(ResponseHeaders(message), request_id)
            await send(message)

        await app(scope, receive, send_with_request_id)

    def assign_request_id(self, ctx: HttpContext) -> str:
        """Determine this request's ID, and store it on the request state.

        Forces a fresh UUID4, or extracts/generates one from the request
        headers, per ``force_generate``. Optionally stores the ID on
        ``ctx.state`` for downstream handlers to read.

        Args:
            ctx (HttpContext): The context to inspect and annotate with a
                request ID.

        Returns:
            str: The request ID assigned to this request.
        """
        if self.force_generate:
            request_id = generate_request_id()
        else:
            request_id = get_request_id_from_header(ctx, self.header_name)
            if not request_id:
                request_id = get_or_generate_request_id(ctx, self.header_name)

        # Not kept on `self`: this middleware instance is shared across every
        # concurrent request the application handles, and a second request's
        # ID landing on `self` between this and `set_response_header` running
        # would echo the wrong ID back on the first request's response.
        # `ctx.state` below is what a caller actually wants -- one per
        # request -- and this method's own return value carries it the rest
        # of the way through this request's `__call__`.
        if self.store_in_request:
            store_request_id_in_request(ctx, request_id, self.request_attribute_name)

        return request_id

    def set_response_header(self, headers: ResponseHeaders, request_id: str) -> None:
        """Echo the request ID back on the outgoing response, if configured to."""
        if not request_id or not self.include_in_response:
            return
        if not headers.headers.get(self.header_name):
            set_request_id_header(headers, request_id, self.header_name)


def RequestId(
    header_name: str = "X-Request-ID",
    force_generate: bool = False,
    store_in_request: bool = True,
    request_attribute_name: str = "request_id",
    include_in_response: bool = True,
) -> RequestIdMiddleware:
    """Factory function that creates a configured RequestIdMiddleware instance.

    Convenience wrapper around ``RequestIdMiddleware`` that provides a
    cleaner API for registering request ID tracking middleware. Accepts
    the same configuration parameters as the middleware constructor
    and returns a fully initialized instance ready for use.

    Args:
        header_name (str, optional): The HTTP header name for reading
            and writing the request ID. Defaults to
            ``"X-Request-ID"``.
        force_generate (bool, optional): When ``True``, always
            generate a new UUID4 regardless of client headers.
            Defaults to ``False``.
        store_in_request (bool, optional): When ``True``, persist the
            request ID on ``ctx.state``. Defaults to ``True``.
        request_attribute_name (str, optional): The attribute name
            used on ``ctx.state`` for storage. Defaults to
            ``"request_id"``.
        include_in_response (bool, optional): When ``True``, include
            the request ID in the response header. Defaults to
            ``True``.

    Returns:
        RequestIdMiddleware: A fully configured middleware instance
            ready to be registered in the middleware pipeline.

    Raises:
        None.
    """
    return RequestIdMiddleware(
        header_name=header_name,
        force_generate=force_generate,
        store_in_request=store_in_request,
        request_attribute_name=request_attribute_name,
        include_in_response=include_in_response,
    )
