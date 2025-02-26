from typing import List, Dict, Any,TypeVar
from .http.request import Request
from .http.response import NexiosResponse
from .http.request import Request
import typing
from functools import wraps
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
        self.allowed_methods.append("OPTIONS")

    def __call__(self, handler: F) -> F:
        if getattr(handler, "_is_wrapped", False):  
            return handler 
        @wraps(handler)
        async def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
            *_, request, response = args  # Ensure request and response are last
            
            if not isinstance(request, Request) or not isinstance(response, NexiosResponse):
                raise TypeError("Expected request and response as the last arguments")

            if request.method.upper() not in self.allowed_methods:
                return response.json(
                    {
                        "error": f"Method {request.method} not allowed",
                        "allowed_methods": self.allowed_methods,
                    },
                    status_code=405,
                )

            return await handler(*args, **kwargs)
        wrapper._is_wrapped = True  # type: ignore
        return wrapper  # type: ignore