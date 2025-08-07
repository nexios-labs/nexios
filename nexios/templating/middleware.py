"""
Template context middleware for Nexios.
"""

from typing import Any, Awaitable, Callable, Dict, Optional

from nexios.middleware import BaseMiddleware
from nexios.types import Request, Response


class TemplateContextMiddleware(BaseMiddleware):
    """Middleware for injecting template context."""

    def __init__(
        self,
        default_context: Optional[Dict[str, Any]] = None,
        context_processor: Optional[
            Callable[[Request], Awaitable[Dict[str, Any]]]
        ] = None,
    ):
        """Initialize middleware with context."""
        self.default_context = default_context or {}
        self.context_processor = context_processor

    async def __call__(
        self,
        request: Request,
        response: Response,
        next: Callable[..., Awaitable[Any]],
    ) -> Response:
        """Process request and inject context."""
        context = self.default_context.copy()

        if self.context_processor:
            request_context = await self.context_processor(request)
            context.update(request_context)

        context.update(
            {
                "request": request,
                "url_for": request.app.url_for,
                "csrf_token":request.state.csrf_token,
            }
        )

        request.state.template_context = context
        return await next()


def template_context(
    default_context: Optional[Dict[str, Any]] = None,
    context_processor: Optional[Callable[[Request], Awaitable[Dict[str, Any]]]] = None,
):
    """Create template context middleware."""
    return TemplateContextMiddleware(default_context, context_processor)
