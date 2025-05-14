from functools import wraps, lru_cache
import asyncio
import time
from typing import Callable, Optional, Awaitable, List, Any, Dict
from nexios.http import Request, Response
from nexios.logging import getLogger

logger = getLogger("nexios")

HandlerType = Callable[..., Awaitable[Response]]


def before_request(
    func: Optional[Callable[[Request, Response], Any]],
    *,
    log_level: Optional[str] = None,
    only_methods: Optional[List[str]] = None,
    for_routes: Optional[str] = None,
) -> None:
    """
    A decorator for before_request hooks with advanced options.

    :param func: The function to run before the request.
    :param log_level: Logging level for the hook (e.g., "INFO", "DEBUG").
    :param only_methods: A list of HTTP methods to apply the hook (e.g., ["POST", "GET"]).
    :param for_routes: A list of specific routes to apply the hook (e.g., ["/api/create/{id}"].
    """

    def decorator(handler: HandlerType) -> HandlerType:
        @wraps(handler)
        async def wrapper(req: Request, res: Response, *args: List[Any], **kwargs: Dict[str, Any]):
           

            if only_methods and req.method.upper() not in map(str.upper, only_methods):
                return await handler(*args, **kwargs)
            if for_routes and req.url.path not in for_routes:
                return await handler(*args, **kwargs)
            if log_level:
                logger.info(f"[{log_level}] Before Request: {req.method} {req.url}")
            if func:
                await func(req, res)
            return await handler(req, res, *args, **kwargs)

        return wrapper

    return decorator  # type:ignore


def after_request(
    func: Optional[Callable[[Request, Response], Any]],
    *,
    log_level: Optional[str] = None,
    only_methods: Optional[List[str]] = None,
    for_routes: Optional[List[str]] = None,
) -> None:
    """
    A decorator for after_request hooks with advanced options.

    :param func: The function to run after the request.
    :param log_level: Logging level for the hook (e.g., "INFO", "DEBUG").
    :param only_methods: A list of HTTP methods to apply the hook (e.g., ["POST", "GET"]).
    :param for_routes: A list of specific routes to apply the hook (e.g., ["/api/create/{id}"].
    """

    def decorator(handler: HandlerType) -> HandlerType:
        @wraps(handler)
        async def wrapper(*args: List[Any], **kwargs: Dict[str, Any]):
            req: Request = args[-2]  # type:ignore
            res: Response = args[-2]  # type:ignore

            response: Response = await handler(*args, **kwargs)
            if only_methods and req.method.upper() not in map(str.upper, only_methods):
                return response
            if for_routes and req.url.path not in for_routes:
                return response
            if log_level:
                logger.info(
                    f"[{log_level}] After Request: {req.method} {req.url} - Status: {response._status_code}"  # type:ignore
                )
            if func:
                await func(req, response)
            return response

        return wrapper

    return decorator  # type:ignore







