from typing import Any, Callable

from nexios.auth.base import AuthenticationBackend, UnauthenticatedUser
from nexios.http import Request, Response


class SessionAuthBackend(AuthenticationBackend):
    """
    Session-based authentication backend that integrates with the framework's
    built-in session manager (req.session).

    This backend checks for authenticated user data in the existing session.
    """

    def __init__(
        self,
        authenticate_func: Callable[..., Any],
        user_key: str = "user",
    ):
        """
        Initialize the session auth backend.

        Args:
            user_key (str): The key used to store user data in the session (default: "user")
        """
        self.user_key = user_key
        self.authenticate_func = authenticate_func

    async def authenticate(self, request: Request, response: Response) -> Any:
        """
        Authenticate the user using the framework's session.

        Args:
            request: The HTTP request containing the session
            response: The HTTP response (unused in this backend)

        Returns:
            Tuple[user_data, "session"] if authenticated
            None if no session exists
            UnauthenticatedUser if session exists but is invalid
        """
        assert "session" in request.scope, "No Session Middleware Installed"
        user_data = request.session.get(self.user_key)
        if not user_data:
            return None

        user = await self.authenticate_func(**user_data)
        if not user:
            return UnauthenticatedUser()
        return user, "session"
