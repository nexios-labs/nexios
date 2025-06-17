import typing
from functools import wraps
from typing import Any, Callable, Dict, List, Tuple, Type, TypeVar, Union

from .http.request import Request
from .http.response import NexiosResponse
from .types import HandlerType

F = TypeVar("F", bound=HandlerType)


class RouteDecorator:
    """Base class for all route decorators"""

    def __init__(self, **kwargs: Dict[str, Any]):
        pass

    def __call__(self, handler: HandlerType) -> Any:
        raise NotImplementedError("Handler not set")

    def __get__(self, obj: typing.Any, objtype: typing.Any = None):
        if obj is None:
            return self
        return self.__class__(obj)  # type:ignore


class allowed_methods(RouteDecorator):
    def __init__(self, methods: List[str]) -> None:
        super().__init__()
        self.allowed_methods: List[str] = [method.upper() for method in methods]

    def __call__(self, handler: F) -> F:
        if getattr(handler, "_is_wrapped", False):
            return handler

        @wraps(handler)
        async def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
            *_, request, response = args  # Ensure request and response are last

            if not isinstance(request, Request) or not isinstance(
                response, NexiosResponse
            ):
                raise TypeError("Expected request and response as the first arguments")

            if request.method.upper() not in self.allowed_methods:
                return response.json(
                    {
                        "error": f"Method {request.method} not allowed",
                        "allowed_methods": self.allowed_methods,
                    },
                    status_code=405,
                    headers={"Allow": ", ".join(self.allowed_methods)},
                )

            return await handler(*args, **kwargs)  # type:ignore

        wrapper._is_wrapped = True  # type: ignore
        return wrapper  # type: ignore


class catch_exception(RouteDecorator):
    """Decorator to catch specific exceptions and handle them with a custom handler"""

    def __init__(
        self,
        exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]],
        handler: Callable[[Exception, Request, NexiosResponse], Any],
    ) -> None:
        super().__init__()
        if not isinstance(exceptions, tuple):
            exceptions = (exceptions,)
        self.exceptions = exceptions
        self.exception_handler = handler

    def __call__(self, handler: F) -> F:
        if getattr(handler, "_is_wrapped", False):
            return handler

        @wraps(handler)
        async def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
            try:
                return await handler(*args, **kwargs)  # type: ignore
            except self.exceptions as e:
                *_, request, response = args

                if not isinstance(request, Request) or not isinstance(
                    response, NexiosResponse
                ):
                    raise TypeError(
                        "Expected request and response as the last arguments"
                    )

                return self.exception_handler(request, response, e)  # type:ignore

        wrapper._is_wrapped = True  # type: ignore
        return wrapper  # type: ignore
