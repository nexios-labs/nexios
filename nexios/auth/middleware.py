from __future__ import annotations

import inspect
from typing_extensions import Annotated, Doc

from .base import AuthenticationBackend, UnauthenticatedUser, BaseUser
from nexios.middlewares.base import BaseMiddleware
from nexios.http import Request, Response
import typing


class AuthenticationMiddleware(BaseMiddleware):
    """
    Middleware responsible for handling user authentication.

    This middleware intercepts incoming HTTP requests, calls the authentication
    backend to verify user credentials, and attaches the authenticated user to
    the request scope.

    Attributes:
        backend (AuthenticationBackend): The authentication backend used to verify users.
    """

    def __init__(
        self,
        backend: Annotated[
            AuthenticationBackend,
            Doc("The authentication backend responsible for verifying users."),
        ],
    ) -> None:
        """
        Initializes the authentication middleware with a specified backend.

        Args:
            backend (AuthenticationBackend): An instance of the authentication backend.
        """
        self.backend = backend

    async def process_request(
        self,
        request: Annotated[
            Request,
            Doc("The HTTP request object, containing authentication credentials."),
        ],
        response: Annotated[
            Response,
            Doc(
                "The HTTP response object, which may be modified during authentication."
            ),
        ],
        call_next: typing.Callable[..., typing.Awaitable[typing.Any]],
    ) -> None:
        """
        Processes an incoming request by authenticating the user.

        This method calls the authentication backend, determines if the user is authenticated,
        and attaches the authenticated user to the request. If authentication fails, the request
        is assigned an `UnauthenticatedUser` instance.

        Args:
            request (Request): The HTTP request object.
            response (Response): The HTTP response object.

        Side Effects:
            - Sets `request.user` to an authenticated user or `UnauthenticatedUser`.
            - Updates `request.scope["user"]` with the user object.

        """
        if not inspect.iscoroutinefunction(self.backend.authenticate):
            user: typing.Tuple[BaseUser, str] = self.backend.authenticate(
                request, response
            )  # type:ignore
        else:
            user: typing.Tuple[BaseUser, str] = await self.backend.authenticate(
                request, response
            )  # type:ignore

        if user is None:  # type:ignore
            request.scope["user"] = UnauthenticatedUser()
            request.scope["auth"] = "no-auth"
            await call_next()

            return

        request.scope["user"] = user[0]
        request.scope["auth"] = user[-1]

        await call_next()
