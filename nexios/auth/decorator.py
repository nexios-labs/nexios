from nexios.decorators import RouteDecorator
import typing
from .exceptions import AuthenticationFailed
from nexios.http import Request, Response
from functools import wraps


class auth(RouteDecorator):

    def __init__(self, scopes: typing.Union[str, typing.List[str], None] = None):
        super().__init__()
        if isinstance(scopes, str):
            self.scopes = [scopes]
        elif scopes is None:
            self.scopes = []  # Allow authentication with any scope
        else:
            self.scopes = scopes

    def __call__(
        self, handler: typing.Callable[..., typing.Awaitable[typing.Any]]
    ) -> typing.Any:

        if getattr(handler, "_is_wrapped", False):
            return handler

        @wraps(handler)  # type: ignore
        async def wrapper(
            *args: typing.List[typing.Any], **kwargs: typing.Dict[str, typing.Any]
        ) -> typing.Any:
            request, response, *_ = kwargs.values()

            if not isinstance(request, Request) or not isinstance(response, Response):
                raise TypeError("Expected request and response as the fist arguments")

            if not request.scope.get("user"):
                raise AuthenticationFailed

            scope = request.scope.get("auth")  # type: ignore

            if self.scopes and scope not in self.scopes:
                raise AuthenticationFailed

            return await handler(*args, **kwargs)

        wrapper._is_wrapped = True  # type: ignore
        return wrapper
