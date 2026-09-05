import re
from collections.abc import Callable
from typing import Any

from sillo.core.http import HttpContext
from sillo.logging import getLogger
from sillo.middleware.response_headers import ResponseHeaders
from sillo.responses import json
from sillo.security.cors.config import CorsConfig
from sillo.types import ASGIApp, Message, Receive, Scope, Send

logger = getLogger()

ALL_METHODS = ("delete", "get", "head", "options", "patch", "post", "put")
BASIC_HEADERS = {"Accept", "Accept-Language", "Content-Language", "Content-Type"}
SAFELISTED_HEADERS = {"accept", "accept-language", "content-language", "content-type"}


class CORSMiddleware:
    """Corsmiddleware"""

    def __init__(self, config: CorsConfig):
        """Init"""
        # Bound on afterwards by `use()`: this is registered as a configured
        # instance, `app.use(CORSMiddleware(config))`.
        self.app: ASGIApp | None = None
        self.config = config
        self.allow_origins: list[str] = self.config.allow_origins or []
        self.blacklist_origins: list[str] = self.config.blacklist_origins or []
        self.allow_methods = self.config.allow_methods or ALL_METHODS
        self.blacklist_headers: list[str] = self.config.blacklist_headers or []
        self.allow_credentials = (
            self.config.allow_credentials
            if self.config.allow_credentials is not None
            else False
        )

        # `*` and credentials cannot be combined. The Fetch standard forbids
        # it, and browsers enforce that by rejecting a literal `*` on a
        # credentialed request — which is why reflecting the caller's Origin
        # instead looks like it works. It does work, and that is the problem:
        # every origin on the internet becomes an allowed one, able to read
        # responses authenticated as the visitor.
        #
        # Refused here rather than quietly downgraded, because both readings
        # of the configuration are plausible — a public API that wants the
        # wildcard, or a credentialed one that wants specific origins — and
        # guessing would leave whoever wrote it believing the other.
        if "*" in self.allow_origins and self.allow_credentials:
            raise ValueError(
                "CORS cannot allow credentials with a wildcard origin.\n\n"
                "Browsers reject `Access-Control-Allow-Origin: *` on a "
                "credentialed request, so allowing both means reflecting "
                "whatever Origin the caller sent — which lets any site read "
                "responses authenticated as your users.\n\n"
                "Name the origins that may send credentials:\n\n"
                "    CorsConfig(\n"
                '        allow_origins=["https://app.example.com"],\n'
                "        allow_credentials=True,\n"
                "    )\n\n"
                "Or keep the wildcard for a public, unauthenticated API and "
                "leave allow_credentials off."
            )

        self.allow_origin_regex = (
            re.compile(self.config.allow_origin_regex)
            if self.config.allow_origin_regex
            else None
        )
        self.allow_headers = self.config.allow_headers or []
        self.expose_headers: list[str] = self.config.expose_headers or []
        self.max_age = self.config.max_age or 600
        self.strict_origin_checking = self.config.strict_origin_checking or False
        self.dynamic_origin_validator: Callable[[str | None], bool] | None = getattr(
            config, "dynamic_origin_validator", None
        )
        self.debug = self.config.debug or False
        self.custom_error_status = self.config.custom_error_status or 400
        self.custom_error_messages: dict[str, Any] = (
            self.config.custom_error_messages or {}
        )
        self._setup_preflight_headers()

    def _setup_preflight_headers(self) -> None:
        """Setup simple and preflight headers."""
        self.simple_headers: dict[str, Any] = {}
        if self.allow_credentials:
            self.simple_headers["Access-Control-Allow-Credentials"] = "true"
        if self.expose_headers:
            self.simple_headers["Access-Control-Expose-Headers"] = ", ".join(
                self.expose_headers
            )

        self.preflight_headers = {
            "Access-Control-Allow-Methods": ", ".join(
                [x.upper() for x in self.allow_methods]
            ),
            "Access-Control-Max-Age": str(self.max_age),
        }
        if self.allow_credentials:
            self.preflight_headers["Access-Control-Allow-Credentials"] = "true"
        if self.allow_headers:
            self.allow_headers: list[str] = [
                *list(SAFELISTED_HEADERS),
                *(self.allow_headers or []),
            ]
        else:
            self.allow_headers = list(SAFELISTED_HEADERS)

    def _inner(self) -> ASGIApp:
        """Return the inner application, refusing to serve without one."""
        if self.app is None:
            raise RuntimeError(
                "CORSMiddleware was constructed without an inner application "
                "and cannot serve requests. Register it with "
                "app.use(CORSMiddleware(...))."
            )
        return self.app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Apply the CORS policy to one connection."""
        app = self._inner()
        if scope["type"] != "http" or not getattr(self, "config", None):
            await app(scope, receive, send)
            return

        ctx = HttpContext(scope, receive)
        origin = ctx.origin

        rejection = await self.check_request(ctx)
        if rejection is not None:
            await rejection(scope, receive, send)
            return

        # Read by the server-error handler if the downstream app blows up
        # before it can stamp its own CORS headers -- an error response is
        # still a response the browser has to be allowed to read.
        server_error_headers = ctx.scope.get("server_error_headers", {})
        server_error_headers["Access-Control-Allow-Origin"] = origin
        ctx.scope["server_error_headers"] = server_error_headers

        async def send_with_cors_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                self.apply_cors_headers(origin, ResponseHeaders(message))
            await send(message)

        await app(scope, receive, send_with_cors_headers)

    async def check_request(self, ctx: HttpContext) -> Any | None:
        """Reject a request missing its Origin under strict checking, or
        answer a preflight outright. `None` means the request carries on to
        the downstream app.
        """
        origin = ctx.origin
        method = ctx.scope["method"]

        if not origin and self.strict_origin_checking:
            if self.debug:
                logger.error("Request denied: Missing 'Origin' header.")
            return json(
                self.get_error_message("missing_origin"),
                status_code=self.custom_error_status,
            )

        if (
            method.lower() == "options"
            and "access-control-request-method" in ctx.headers
        ):
            return await self.preflight_response(ctx)

        return None

    def apply_cors_headers(self, origin: str | None, headers: ResponseHeaders) -> None:
        """Stamp the CORS headers onto a response that ran the downstream app."""
        if origin and self.is_allowed_origin(origin):
            headers.set_header(
                "Access-Control-Allow-Origin",
                self.allow_origin_value(origin),
                override=True,
            )

            if self.allow_credentials:
                headers.set_header(
                    "Access-Control-Allow-Credentials", "true", override=True
                )

        if self.expose_headers:
            headers.set_header(
                "Access-Control-Expose-Headers",
                ", ".join(self.expose_headers),
                override=True,
            )

    def allow_origin_value(self, origin: str) -> str:
        """What to send back in ``Access-Control-Allow-Origin``.

        A wildcard configuration answers with the literal ``*`` rather than
        the caller's own origin. Both satisfy the browser, but echoing the
        origin makes the response vary by caller — which turns any shared
        cache in front of the application into somewhere one origin's headers
        can be served to another. Credentials are already ruled out alongside
        a wildcard, so nothing needs the specific form here.
        """
        if "*" in self.allow_origins and not self.allow_credentials:
            return "*"

        return origin

    def is_allowed_origin(self, origin: str | None) -> bool:
        """Is Allowed Origin"""
        if origin in self.blacklist_origins:
            if self.debug:
                logger.error(f"Request denied: Origin '{origin}' is blacklisted.")

            return False

        if "*" in self.allow_origins:
            return True
        try:
            if self.allow_origin_regex and self.allow_origin_regex.fullmatch(origin):  # ty: ignore
                return True
        except re.error:
            return False

        if self.dynamic_origin_validator and callable(self.dynamic_origin_validator):
            return self.dynamic_origin_validator(origin)

        return origin in self.allow_origins

    def is_allowed_method(self, method: str | None) -> bool:
        """Is Allowed Method"""
        if not method or method.strip() == "":
            return False
        if "*" in self.allow_methods:
            return True
        return method.lower() in [x.lower() for x in self.allow_methods]

    async def preflight_response(self, ctx: HttpContext) -> Any:
        """Preflight Response"""
        origin = ctx.headers.get("origin")
        requested_method = ctx.headers.get("access-control-request-method")
        requested_headers = ctx.headers.get("access-control-request-headers")

        headers = {}

        if not self.is_allowed_origin(origin):
            if self.debug:
                logger.error(
                    f"Preflight request denied: Origin '{origin}' is not allowed."
                )
            return json(
                self.get_error_message("disallowed_origin"),
                status_code=self.custom_error_status,
            )

        if origin:
            headers["Access-Control-Allow-Origin"] = self.allow_origin_value(origin)

        if not self.is_allowed_method(requested_method):
            if self.debug:
                logger.error(
                    f"Preflight request denied: Method '{requested_method}' is not allowed."
                )
            return json(
                self.get_error_message("disallowed_method"),
                status_code=self.custom_error_status,
            )

        if requested_method:
            headers["Access-Control-Allow-Methods"] = requested_method.upper()

        if requested_headers:
            requested_header_list = [
                h.strip().lower() for h in requested_headers.split(",")
            ]

            allowed_requested_headers = []
            for header in requested_header_list:
                # If allow_headers is "*", allow any header (except blacklisted)
                if "*" in self.config.allow_headers:
                    if header in self.blacklist_headers:
                        if self.debug:
                            logger.error(
                                f"Preflight request denied: Header '{header}' is blacklisted."
                            )
                        return json(
                            self.get_error_message("disallowed_header"),
                            status_code=self.custom_error_status,
                        )
                else:
                    if (
                        header not in [x.lower() for x in self.allow_headers]
                        or header in self.blacklist_headers
                    ):
                        if self.debug:
                            logger.error(
                                f"Preflight request denied: Header '{header}' is not allowed."
                            )
                        return json(
                            self.get_error_message("disallowed_header"),
                            status_code=self.custom_error_status,
                        )
                allowed_requested_headers.append(header)

            if allowed_requested_headers:
                headers["Access-Control-Allow-Headers"] = ", ".join(
                    allowed_requested_headers
                )

        headers["Access-Control-Max-Age"] = str(self.max_age)
        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

        return json("OK", status_code=201, headers=headers)

    def get_error_message(self, error_type: str) -> str:
        """Get Error Message"""
        if not self.custom_error_messages:
            return "CORS request denied."
        return self.custom_error_messages.get(error_type, "CORS request denied.")
