try:
    import jwt
except ImportError:
    raise ImportError("Install PyJWT to use JWT authentication backend")

from typing import Optional, Dict, Any, List, Callable, Awaitable
from typing_extensions import Annotated, Doc
from nexios.auth.base import AuthenticationBackend, UnauthenticatedUser
from nexios.http import Request, Response
from nexios.config import get_config


def create_jwt(
    payload: Annotated[
        Dict[str, Any],
        Doc("The data to include in the JWT payload."),
    ],
    secret: Annotated[
        Optional[str],
        Doc(
            "The secret key used to sign the token. If not provided, the application's default secret key is used."
        ),
    ] = None,
    algorithm: Annotated[
        str,
        Doc("The algorithm used to sign the JWT token. Default is 'HS256'."),
    ] = "HS256",
) -> str:
    """
    Creates a signed JWT token.

    Args:
        payload (Dict[str, Any]): The data to encode in the token.
        secret (Optional[str]): The secret key for signing. Defaults to app's config secret.
        algorithm (str): The signing algorithm (default: "HS256").

    Returns:
        str: The encoded JWT token.
    """
    secret = secret or get_config().secret_key
    return jwt.encode(payload, secret, algorithm=algorithm)  # type: ignore


def decode_jwt(
    token: Annotated[
        str,
        Doc("The JWT token to be decoded."),
    ],
    secret: Annotated[
        str,
        Doc("The secret key that was used to sign the token."),
    ],
    algorithms: Annotated[
        List[str],
        Doc("A list of allowed algorithms for decoding the token."),
    ],
) -> Dict[str, Any]:
    """
    Decodes a JWT token and verifies its validity.

    Args:
        token (str): The encoded JWT token.
        secret (str): The secret key for verification.
        algorithms (List[str]): List of acceptable algorithms for decoding.

    Returns:
        Dict[str, Any]: The decoded payload of the JWT.

    Raises:
        ValueError: If the token is expired or invalid.
    """
    try:
        return jwt.decode(token, secret, algorithms=algorithms)  # type: ignore
    except jwt.ExpiredSignatureError:  # type: ignore
        raise ValueError("Token has expired")  # type: ignore
    except jwt.InvalidTokenError:  # type: ignore
        raise ValueError("Invalid token")


class JWTAuthBackend(AuthenticationBackend):
    """
    Authentication backend for JWT (JSON Web Token) authentication.

    This backend extracts the JWT from the `Authorization` header,
    decodes it using a configured secret and algorithm, and validates
    the token. If valid, the associated user is retrieved via a
    user-defined authentication function.

    Attributes:
        authenticate_func (Callable[..., Awaitable[Any]]):
            A function that takes decoded token data and returns a user object if valid.
    """

    def __init__(
        self,
        authenticate_func: Annotated[
            Callable[..., Awaitable[Any]],
            Doc(
                "A function that takes decoded JWT payload and returns a user object if valid."
            ),
        ],
    ) -> None:
        """
        Initializes the JWT authentication backend.

        Args:
            authenticate_func (Callable[..., Awaitable[Any]]):
                A function to authenticate users based on JWT payload data.
        """
        self.authenticate_func = authenticate_func

    async def authenticate(  # type: ignore
        self,
        request: Annotated[
            Request,
            Doc(
                "The HTTP request containing the JWT token in the `Authorization` header."
            ),
        ],
        response: Annotated[
            Response,
            Doc(
                "The HTTP response object, which may be modified if authentication fails."
            ),
        ],
    ) -> Any:
        """
        Authenticates a request using JWT.

        This method extracts the JWT from the request header,
        verifies it, and retrieves the associated user.

        Args:
            request (Request): The incoming HTTP request.
            response (Response): The response object (may be modified).

        Returns:
            Any: A user object if authentication is successful,
            `UnauthenticatedUser` if authentication fails, or `None` if no token is provided.

        Side Effects:
            - If no valid JWT is found, the `WWW-Authenticate` header is set in the response.
        """
        app_config = get_config()
        self.secret = app_config.secret_key
        self.algorithms = app_config.jwt_algorithms or ["HS256"]

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            response.header("WWW-Authenticate",'Bearer realm="Access to the API"')
            return None

        token = auth_header.split(" ")[1]
        try:
            payload = decode_jwt(token, self.secret, self.algorithms)
        except ValueError:
            return None

        user: Any = await self.authenticate_func(**payload)
        if not user:
            return UnauthenticatedUser()

        return user,"httpauth"
