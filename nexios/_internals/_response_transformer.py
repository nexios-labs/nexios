import asyncio
import typing

from nexios.dependencies import Context, current_context
from nexios.http import Request, Response
from nexios.http.response import BaseResponse
from nexios.types import ASGIApp, Receive, Scope, Send
from nexios.utils.async_helpers import is_async_callable
from nexios.utils.concurrency import run_in_threadpool


async def request_response(
    func: typing.Callable[[Request, Response], typing.Awaitable[Response]],
) -> ASGIApp:
    """
    Takes a function or coroutine `func(request) -> response`,
    and returns an ASGI application.
    """
    assert asyncio.iscoroutinefunction(func), "Endpoints must be async"

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        response_manager = Response._instance
        if not response_manager:
            request = Request(scope, receive, send)
            response_manager = Response(request)
        else:
            request = response_manager._request

        ctx = Context(
            request=request,
            response=response_manager,
            user=getattr(request, "user", None),
            app=request.app,
            base_app=getattr(request, "base_app", None),
            )
        token = current_context.set(ctx)
        try:
           
            if is_async_callable(func):
                func_result = await func(request, response_manager, **request.path_params)
            else:
                func_result = await run_in_threadpool(
                    func, request, response_manager, **request.path_params
                )
        finally:
            current_context.reset(token)
        if isinstance(func_result, (dict, list, str)):
            response_manager.json(func_result)

        elif isinstance(func_result, BaseResponse):
            response_manager.make_response(func_result)
        response = response_manager.get_response()
        return await response(scope, receive, send)

    return app
