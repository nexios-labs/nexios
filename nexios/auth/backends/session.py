from typing import Any

from nexios.auth.base import AuthenticationBackend
from nexios.http import Request, Response
from nexios.auth.model import AuthResult


class SessionAuthBackend(AuthenticationBackend):
    """
    Session-based authentication backend that integrates with the framework's
    built-in session manager (req.session).

    This backend checks for authenticated user data in the existing session.
    """

    # def __init__(
    #     self,
    #     authenticate_func: Callable[..., Any],
    #     user_key: str = "user",
    # ):
    #     """
    #     Initialize the session auth backend.

    #     Args:
    #         user_key (str): The key used to store user data in the session (default: "user")
    #     """
    #     self.user_key = user_key
    #     self.authenticate_func = authenticate_func

    async def authenticate(self, request: Request, response: Response) -> Any:
        """
        Authenticate the user using the framework's session.

        Args:
            request: The HTTP request containing the session
            response: The HTTP response (unused in this backend)

        Raises:
            AuthenticationError: If the user is not authenticated
        Returns:
            AuthResult: An authenticated user object if authentication succeeds.
        """
        assert "session" in request.scope, "No Session Middleware Installed"
        user_data = request.session.get("user")
        if not user_data:
            return AuthResult(success=False, identity="", scope="")

      
        return AuthResult(success=True, identity=user_data.get("id", ""), scope="session")
