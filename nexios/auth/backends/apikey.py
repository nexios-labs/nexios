from typing import Any, Awaitable, Callable

from typing_extensions import Annotated, Doc

from nexios.auth.base import AuthenticationBackend, UnauthenticatedUser
from nexios.http import Request, Response


class APIKeyAuthBackend(AuthenticationBackend):
    """
    Authentication backend for API key-based authentication.

    This class verifies incoming requests using API keys found in request headers.
    It relies on a user-defined authentication function to validate API keys.

    Attributes:
        authenticate_func (Callable[..., Awaitable[Any]]): The function used to validate API keys.
        header_name (str): The HTTP header used to pass the API key (default: "X-API-Key").
    """

    def __init__(
        self,
        authenticate_func: Annotated[
            Callable[..., Awaitable[Any]],
            Doc(
                "Function that takes an API key and returns a user object if valid, None otherwise."
            ),
        ],
        header_name: Annotated[
            str,
            Doc(
                'The header name from which the API key is retrieved (default: "X-API-Key").'
            ),
        ] = "X-API-Key",
    ) -> None:
        """
        Initializes the APIKeyAuthBackend with an authentication function and optional header name.

        Args:
            authenticate_func (Callable[..., Awaitable[Any]]): Function to validate API keys.
            header_name (str, optional): Header key where the API key is expected (default: "X-API-Key").
        """
        self.authenticate_func = authenticate_func
        self.header_name = header_name

    async def authenticate(  # type: ignore[override]
        self,
        request: Annotated[
            Request,
            Doc(
                "The incoming HTTP request, containing authentication credentials in headers."
            ),
        ],
        response: Annotated[
            Response,
            Doc(
                "The HTTP response object, which may be modified for authentication-related headers."
            ),
        ],
    ) -> Any:
        """
        Authenticates the request by checking for an API key in the specified header.

        This method extracts the API key from the request headers and verifies it
        using the provided authentication function.

        Args:
            request (Request): The incoming HTTP request.
            response (Response): The response object (may be modified).

        Returns:
            Any: A user object if authentication is successful, `UnauthenticatedUser` if invalid, or `None` if no API key is provided.

        Side Effects:
            - If no API key is found, sets the `WWW-Authenticate` response header.
        """
        # Retrieve the API key from the request headers
        api_key = request.headers.get(self.header_name)
        if not api_key:
            response.set_header("WWW-Authenticate", 'APIKey realm="Access to the API"')
            return None

        # Authenticate the API key using the provided function
        user = await self.authenticate_func(api_key)
        if not user:
            return UnauthenticatedUser()

        return user, "apikey"
