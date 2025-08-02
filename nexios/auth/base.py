from __future__ import annotations

import typing

from typing_extensions import Annotated, Doc

from nexios.http import Request, Response


class AuthenticationError(Exception):
    """
    Exception raised when authentication fails.

    This error is triggered when an authentication backend determines that
    the provided credentials are invalid or the authentication process
    encounters an unexpected issue.
    """

    pass


class AuthCredentials:
    def __init__(self, scopes: typing.Optional[typing.Sequence[str]] = None):
        self.scopes = [] if scopes is None else list(scopes)


class AuthenticationBackend:
    """
    Base class for authentication backends in Nexios.

    Authentication backends are responsible for verifying user credentials
    and returning an authenticated user instance if authentication is successful.

    Subclasses must override `authenticate()` to implement custom authentication logic.
    """

    async def authenticate(
        self,
        req: Annotated[
            Request, Doc("The incoming HTTP request containing authentication details.")
        ],
        res: Annotated[
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


class BaseUser:
    """
    Abstract base class for user objects.

    This class defines the minimum required properties for user objects,
    including authentication status, display name, and identity.

    Subclasses should override these properties to provide meaningful values.
    """

    @property
    def is_authenticated(
        self,
    ) -> Annotated[bool, Doc("Indicates whether the user is authenticated.")]:
        """
        Checks if the user is authenticated.

        This property should be overridden in subclasses to return `True` for
        authenticated users and `False` for unauthenticated users.

        Returns:
            bool: `True` if the user is authenticated, otherwise `False`.
        """
        raise NotImplementedError()

    @property
    def display_name(
        self,
    ) -> Annotated[str, Doc("The name to be displayed for the user.")]:
        """
        Retrieves the display name of the user.

        This property should be overridden to return a human-readable
        name for authenticated users or an empty string for unauthenticated users.

        Returns:
            str: The display name of the user.
        """
        raise NotImplementedError()

    @property
    def identity(
        self,
    ) -> Annotated[
        str, Doc("A unique identifier for the user, such as a username or ID.")
    ]:
        """
        Retrieves the unique identity of the user.

        This property should be overridden to return a unique identifier
        (e.g., username, email, or user ID).

        Returns:
            str: The unique identifier of the user.
        """
        raise NotImplementedError()
    def has_permission(self, permission :str):
        """checks if the request user has the provided permission"""



class SimpleUser(BaseUser):
    """
    A basic implementation of an authenticated user.

    This class represents a simple authenticated user with a username.
    """

    def __init__(
        self, 
        username: Annotated[str, Doc("The username of the authenticated user.")],
        permissions = Annotated[str, Doc("Array of user User Permissions")]
    ) -> None:
        """
        Initializes a simple authenticated user.

        Args:
            username (str): The username of the user.
        """
        self.username = username
        self.permissions = permissions

    @property
    def is_authenticated(
        self,
    ) -> Annotated[
        bool, Doc("Always returns `True` since this user is authenticated.")
    ]:
        """
        Indicates that the user is authenticated.

        Returns:
            bool: Always `True` since this represents an authenticated user.
        """
        return True

    @property
    def display_name(
        self,
    ) -> Annotated[str, Doc("Returns the username as the display name.")]:
        """
        Retrieves the display name of the user.

        Returns:
            str: The username of the authenticated user.
        """
        return self.username
    def has_permission(self, permission: str):
        return permission in self.permissions


class UnauthenticatedUser(BaseUser):
    """
    Represents an unauthenticated user.

    This class is used to represent users who have not logged in.
    """

    @property
    def is_authenticated(
        self,
    ) -> Annotated[
        bool, Doc("Always returns `False` since this user is unauthenticated.")
    ]:
        """
        Indicates that the user is not authenticated.

        Returns:
            bool: Always `False` since this represents an unauthenticated user.
        """
        return False

    @property
    def display_name(
        self,
    ) -> Annotated[
        str,
        Doc(
            "Returns an empty string since unauthenticated users have no display name."
        ),
    ]:
        """
        Retrieves the display name of the user.

        Since unauthenticated users do not have a valid username, this
        method returns an empty string.

        Returns:
            str: An empty string.
        """
        return ""
