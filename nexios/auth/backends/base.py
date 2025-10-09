from __future__ import annotations

import typing

from typing_extensions import Annotated, Doc

from nexios.http import Request, Response






class AuthenticationBackend:
    """
    Base class for authentication backends in Nexios.

    Authentication backends are responsible for verifying user credentials
    and returning an authenticated user instance if authentication is successful.

    Subclasses must override `authenticate()` to implement custom authentication logic.
    """

    async def authenticate(
        self,
        request: Annotated[
            Request, Doc("The incoming HTTP request containing authentication details.")
        ],
        response: Annotated[
            Response,
            Doc("The HTTP response object that may be modified during authentication."),
        ],
    ) -> Annotated[
        typing.Any,
        Doc("Returns an authenticated user instance or raises an AuthenticationError."),
    ]:
        """
        Authenticates a user based on the request.

        Subclasses must implement this method to verify authentication credentials
        (e.g., headers, cookies, or tokens) and return an authenticated user instance.

        Args:
            req (Request): The HTTP request object.
            res (Response): The HTTP response object.

        Returns:
            Any: An authenticated user object if authentication succeeds.

        Raises:
            AuthenticationError: If authentication fails.
        """
        raise NotImplementedError()








