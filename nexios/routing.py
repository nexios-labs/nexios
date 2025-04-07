from __future__ import annotations
from token import OP
from typing import (
    Any,
    List,
    Optional,
    Pattern,
    Dict,
    TypeVar,
    Tuple,
    Callable,
    Union,
    Type,
)
from dataclasses import dataclass
import re
import copy
import warnings, typing
from enum import Enum
from abc import abstractmethod, ABC

from nexios.openapi.models import Parameter, Path, Schema
from nexios.types import MiddlewareType, WsMiddlewareType, HandlerType, WsHandlerType
from nexios.decorators import allowed_methods
from typing_extensions import Doc, Annotated  # type: ignore
from nexios.structs import URLPath, RouteParam
from nexios.http import Request, Response
from nexios.http.response import JSONResponse
from nexios.types import Scope, Send, Receive, ASGIApp
from .routing_utils import Convertor, CONVERTOR_TYPES, get_route_path
from nexios.websockets import WebSocket
from nexios.middlewares.core import BaseMiddleware
from nexios.middlewares.core import Middleware, wrap_middleware
from nexios.exceptions import NotFoundException
from nexios.websockets.errors import WebSocketErrorMiddleware
from pydantic import BaseModel


T = TypeVar("T")
allowed_methods_default = ["get", "post", "delete", "put", "patch", "options"]


def request_response(
    func: typing.Callable[[Request, Response], typing.Awaitable[Response]],
) -> ASGIApp:
    """
    Takes a function or coroutine `func(request) -> response`,
    and returns an ASGI application.
    """

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive, send)
        response_manager = Response()

        await func(request, response_manager)
        response = response_manager.get_response()
        return await response(scope, receive, send)

    return app


def websocket_session(
    func: typing.Callable[[WebSocket], typing.Awaitable[None]],
) -> ASGIApp:
    """
    Takes a coroutine `func(session)`, and returns an ASGI application.
    """
    # assert asyncio.iscoroutinefunction(func), "WebSocket endpoints must be async"

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        session = WebSocket(scope, receive=receive, send=send)

        async def app(scope: Scope, receive: Receive, send: Send) -> None:
            await func(session)

        # await wrap_app_handling_exceptions(app, session)(scope, receive, send)
        await app(scope, receive, send)

    return app


def replace_params(
    path: str,
    param_convertors: dict[str, Convertor[typing.Any]],
    path_params: dict[str, str],
) -> tuple[str, dict[str, str]]:
    for key, value in list(path_params.items()):
        if "{" + key + "}" in path:
            convertor = param_convertors[key]
            value = convertor.to_string(value)
            path = path.replace("{" + key + "}", value)
            path_params.pop(key)
    return path, path_params


# Match parameters in URL paths, eg. '{param}', and '{param:int}'
PARAM_REGEX = re.compile("{([a-zA-Z_][a-zA-Z0-9_]*)(:[a-zA-Z_][a-zA-Z0-9_]*)?}")


def compile_path(
    path: str,
) -> tuple[typing.Pattern[str], str, dict[str, Convertor[typing.Any]]]:
    """
    Given a path string, like: "/{username:str}",
    or a host string, like: "{subdomain}.mydomain.org", return a three-tuple
    of (regex, format, {param_name:convertor}).

    regex:      "/(?P<username>[^/]+)"
    format:     "/{username}"
    convertors: {"username": StringConvertor()}
    """
    is_host = not path.startswith("/")

    path_regex = "^"
    path_format = ""
    duplicated_params: typing.Set[typing.Any] = set()

    idx = 0
    param_convertors = {}
    param_names: List[str] = []
    for match in PARAM_REGEX.finditer(path):
        param_name, convertor_type = match.groups("str")
        convertor_type = convertor_type.lstrip(":")
        assert (
            convertor_type in CONVERTOR_TYPES
        ), f"Unknown path convertor '{convertor_type}'"
        convertor = CONVERTOR_TYPES[convertor_type]

        path_regex += re.escape(path[idx : match.start()])
        path_regex += f"(?P<{param_name}>{convertor.regex})"
        path_format += path[idx : match.start()]
        path_format += "{%s}" % param_name

        if param_name in param_convertors:
            duplicated_params.add(param_name)

        param_convertors[param_name] = convertor

        idx = match.end()
        param_names.append(param_name)

    if duplicated_params:
        names = ", ".join(sorted(duplicated_params))
        ending = "s" if len(duplicated_params) > 1 else ""
        raise ValueError(f"Duplicated param name{ending} {names} at path {path}")

    if is_host:
        # Align with `Host.matches()` behavior, which ignores port.
        hostname = path[idx:].split(":")[0]
        path_regex += re.escape(hostname) + "$"
    else:
        path_regex += re.escape(path[idx:]) + "$"
    path_format += path[idx:]

    return re.compile(path_regex), path_format, param_convertors, param_names  # type: ignore


class RouteType(Enum):
    REGEX = "regex"
    PATH = "path"
    WILDCARD = "wildcard"


@dataclass
class RoutePattern:
    """Represents a processed route pattern with metadata"""

    pattern: Pattern[str]
    raw_path: str
    param_names: List[str]
    route_type: RouteType
    convertor: Convertor[Any]


class RouteBuilder:
    @staticmethod
    def create_pattern(path: str) -> RoutePattern:
        path_regex, path_format, param_convertors, param_names = (
            compile_path(  # type:ignore #REVIEW
                path
            )
        )
        return RoutePattern(
            pattern=path_regex,
            raw_path=path,
            param_names=param_names,
            route_type=path_format,  # type:ignore
            convertor=param_convertors,  # type:ignore
        )


class BaseRouter(ABC):
    """
    Base class for routers. This class should not be instantiated directly.
    Subclasses should implement the `__call__` method to handle specific routing logic.
    """

    def __init__(self, prefix: Optional[str] = None):
        self.prefix = prefix or ""
        self.routes: List[Any] = []
        self.middlewares: List[Any] = []
        self.sub_routers: Dict[str, ASGIApp] = {}

        if self.prefix and not self.prefix.startswith("/"):
            warnings.warn("Router prefix should start with '/'")
            self.prefix = f"/{self.prefix}"

    @abstractmethod
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Abstract method to handle incoming requests. Subclasses must implement this method.

        Args:
            scope: The ASGI scope dictionary.
            receive: The ASGI receive callable.
            send: The ASGI send callable.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def add_middleware(self, middleware: MiddlewareType) -> None:
        """
        Add middleware to the router.

        Args:
            middleware: The middleware to add.
        """

        self.middlewares.append(middleware)

    def build_middleware_stack(self, app: ASGIApp) -> ASGIApp:
        """
        Builds the middleware stack by applying all registered middlewares to the app.

        Args:
            app: The base ASGI application.

        Returns:
            ASGIApp: The application wrapped with all middlewares.
        """
        for mdw in reversed(self.middlewares):
            app = mdw(app)
        return app

    def mount_router(
        self, app: Union["Router", "WSRouter"], path: Optional[str] = None
    ) -> None:
        """
        Mount an ASGI application (e.g., another Router) under a specific path prefix.

        Args:
            path: The path prefix under which the app will be mounted.
            app: The ASGI application (e.g., another Router) to mount.
        """
        if not path:
            path = app.prefix
        path = path.rstrip("/")

        if path == "":
            self.sub_routers[path] = app
            return
        if not path.startswith("/"):
            path = f"/{path}"

        self.sub_routers[path] = app

    def __repr__(self) -> str:
        return f"<BaseRouter prefix='{self.prefix}' routes={len(self.routes)}>"


class Routes:
    """
    Encapsulates all routing information for an API endpoint, including path handling,
    validation, OpenAPI documentation, and request processing.

    Attributes:
        raw_path: The original URL path string provided during initialization.
        pattern: Compiled regex pattern for path matching.
        handler: Callable that processes incoming requests.
        methods: List of allowed HTTP methods for this endpoint.
        validator: Request parameter validation rules.
        request_schema: Schema for request body documentation.
        response_schema: Schema for response documentation.
        deprecated: Deprecation status indicator.
        tags: OpenAPI documentation tags.
        description: Endpoint functionality details.
        summary: Concise endpoint purpose.
    """

    def __init__(
        self,
        path: Annotated[
            str,
            Doc(
                """
            URL path pattern for the endpoint. Supports dynamic parameters using curly brace syntax.
            Examples:
            - '/users' (static path)
            - '/posts/{id}' (path parameter)
            - '/files/{filepath:.*}' (regex-matched path parameter)
            """
            ),
        ],
        handler: Annotated[
            Optional[HandlerType],
            Doc(
                """
            Callable responsible for processing requests to this endpoint. Can be:
            - A regular function
            - An async function
            - A class method
            - Any object implementing __call__

            The handler should accept a request object and return a response object.
            Example: def user_handler(request: Request) -> Response: ...
            """
            ),
        ],
        methods: Annotated[
            Optional[List[str]],
            Doc(
                """
            HTTP methods allowed for this endpoint. Common methods include:
            - GET: Retrieve resources
            - POST: Create resources
            - PUT: Update resources
            - DELETE: Remove resources
            - PATCH: Partial updatess

            Defaults to ['GET'] if not specified. Use uppercase method names.
            """
            ),
        ] = None,
        name: Annotated[
            Optional[str],
            Doc(
                """The unique identifier for the route. This name is used to generate 
            URLs dynamically with `url_for`. It should be a valid, unique string 
            that represents the route within the application."""
            ),
        ] = None,
        summary: Annotated[
            Optional[str],
            Doc(
                "A brief summary of the API endpoint. This should be a short, one-line description providing a high-level overview of its purpose."
            ),
        ] = None,
        description: Annotated[
            Optional[str],
            Doc(
                "A detailed explanation of the API endpoint, including functionality, expected behavior, and additional context."
            ),
        ] = None,
        responses: Annotated[
            Optional[Dict[int, Any]],
            Doc(
                "A dictionary mapping HTTP status codes to response schemas or descriptions. Keys are HTTP status codes (e.g., 200, 400), and values define the response format."
            ),
        ] = None,
        request_model: Annotated[
            Optional[Type[BaseModel]],
            Doc(
                "A Pydantic model representing the expected request payload. Defines the structure and validation rules for incoming request data."
            ),
        ] = None,
        response_model: Optional[Type[BaseModel]] = None,
        tags: Optional[List[str]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
        operation_id: Optional[str] = None,
        deprecated: bool = False,
        parameters: List[Parameter] = [],
        middlewares: List[Any] = [],
        exclude_from_schema: bool = False,
        **kwargs: Dict[str, Any],
    ):
        """
        Initialize a route configuration with endpoint details.

        Args:
            path: URL path pattern with optional parameters.
            handler: Request processing function/method.
            methods: Allowed HTTP methods (default: ['GET']).
            validator: Multi-layer request validation rules.
            request_schema: Request body structure definition.
            response_schema: Success response structure definition.
            deprecated: Deprecation marker.
            tags: Documentation categories.
            description: Comprehensive endpoint documentation.
            summary: Brief endpoint description.

        Raises:
            AssertionError: If handler is not callable.
        """
        assert callable(handler), "Route handler must be callable"
        from nexios.openapi._builder import APIDocumentation

        self.prefix = None
        self.docs = APIDocumentation.get_instance()

        self.raw_path = path
        self.handler = handler
        self.methods = methods or allowed_methods_default
        self.name = name

        self.route_info = RouteBuilder.create_pattern(path)
        self.pattern: Pattern[str] = self.route_info.pattern
        self.param_names = self.route_info.param_names
        self.route_type = self.route_info.route_type
        self.middlewares: typing.List[MiddlewareType] = list(middlewares)
        self.summary = summary
        self.description = description
        self.responses = responses
        self.request_model = request_model
        self.kwargs = kwargs
        self.tags = tags
        self.security = security
        self.operation_id = operation_id
        self.deprecated = deprecated
        self.parameters = parameters
        self.exlude_from_schema = exclude_from_schema

    def match(self, path: str, method: str) -> typing.Tuple[Any, Any, Any]:
        """
        Match a path against this route's pattern and return captured parameters.

        Args:
            path: The URL path to match.

        Returns:
            Optional[Dict[str, Any]]: A dictionary of captured parameters if the path matches,
            otherwise None.
        """
        match = self.pattern.match(path)
        if match:
            matched_params = match.groupdict()
            for key, value in matched_params.items():
                matched_params[key] = self.route_info.convertor[
                    key
                ].convert(  # type:ignore
                    value
                )  # type:ignore
            is_method_allowed = method.lower() in [m.lower() for m in self.methods]
            return match, matched_params, is_method_allowed
        return None, None, False

    def url_path_for(self, _name: str, **path_params: Any) -> URLPath:
        """
        Generate a URL path for the route with the given name and parameters.

        Args:
            name: The name of the route.
            path_params: A dictionary of path parameters to substitute into the route's path.

        Returns:
            str: The generated URL path.

        Raises:
            ValueError: If the route name does not match or if required parameters are missing.
        """
        if _name != self.name:
            raise ValueError(
                f"Route name '{_name}' does not match the current route name '{self.name}'."
            )

        required_params = set(self.param_names)
        provided_params = set(path_params.keys())
        if required_params != provided_params:
            missing_params = required_params - provided_params
            extra_params = provided_params - required_params
            raise ValueError(
                f"Missing parameters: {missing_params}. Extra parameters: {extra_params}."
            )

        path = self.raw_path
        for param_name, param_value in path_params.items():
            param_value = str(param_value)

            path = re.sub(rf"\{{{param_name}(:[^}}]+)?}}", param_value, path)

        return URLPath(path=path, protocol="http")

    async def handle(self, scope: Scope, receive: Receive, send: Send) -> Any:
        """
        Process an incoming request using the route's handler.

        Args:
            request: The incoming HTTP request object.
            response: The outgoing HTTP response object.

        Returns:
            Response: The processed HTTP response object.
        """

        async def apply_middlewares(app: ASGIApp) -> ASGIApp:
            middleware: typing.List[Middleware] = []
            for mdw in self.middlewares:
                middleware.append(wrap_middleware(mdw))  # type: ignore
            for cls, args, kwargs in reversed(middleware):
                app = cls(app, *args, **kwargs)
            return app

        app = await apply_middlewares(request_response(self.handler))

        await app(scope, receive, send)

    def __call__(self) -> Tuple[Pattern[str], HandlerType]:
        """
        Return the route components for registration.

        Returns:
            Tuple[Pattern[str], HandlerType]: The compiled regex pattern and the handler.

        """
        return self.pattern, self.handler

    def __repr__(self) -> str:
        """
        Return a string representation of the route.

        Returns:
            str: A string describing the route.
        """
        return f"<Route {self.raw_path} methods={self.methods}>"


class Router(BaseRouter):
    def __init__(
        self,
        prefix: Optional[str] = None,
        routes: Optional[List[Routes]] = None,
        tags: Optional[List[str]] = None,
        exclude_from_schema: bool = False,
    ):
        self.prefix = prefix or ""
        self.prefix.rstrip("/")
        self.routes: List[Routes] = list(routes) if routes else []
        self.middlewares: typing.List[Middleware] = []
        self.sub_routers: Dict[str, ASGIApp] = {}
        self.route_class = Routes
        self.tags = tags or []
        self.exclude_from_schema = exclude_from_schema

        if self.prefix and not self.prefix.startswith("/"):
            warnings.warn("Router prefix should start with '/'")
            self.prefix = f"/{self.prefix}"

    def build_middleware_stack(self, app: ASGIApp) -> ASGIApp:
        """
        Builds the middleware stack by applying all registered middlewares to the app.

        Args:
            app: The base ASGI application.

        Returns:
            ASGIApp: The application wrapped with all middlewares.
        """
        for cls, args, kwargs in reversed(self.middlewares):
            app = cls(app, *args, **kwargs)
        return app

    def add_route(
        self,
        route: Annotated[
            Routes, Doc("An instance of the Routes class representing an HTTP route.")
        ],
    ) -> None:
        """
        Adds an HTTP route to the application.

        This method registers an HTTP route, allowing the application to handle requests for a specific URL path.

        Args:
            route (Routes): The HTTP route configuration.

        Returns:
            None

        Example:
            ```python
            route = Routes("/home", home_handler, methods=["GET", "POST"])
            app.add_route(route)
            ```
        """
        route.tags = self.tags + route.tags if route.tags else self.tags
        if self.exclude_from_schema:
            route.exlude_from_schema = True
        self.routes.append(route)

    def add_middleware(self, middleware: MiddlewareType) -> None:
        """Add middleware to the router"""
        if callable(middleware):
            mdw = Middleware(BaseMiddleware, dispatch=middleware)  # type: ignore
            self.middlewares.insert(0, mdw)

    def get(
        self,
        path: str,
        handler: Optional[HandlerType] = None,
        name: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        responses: Optional[Dict[int, Any]] = None,
        request_model: Optional[Type[BaseModel]] = None,
        middlewares: List[Any] = [],
        tags: Optional[List[str]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
        operation_id: Optional[str] = None,
        deprecated: bool = False,
        parameters: List[Parameter] = [],
        exclude_from_schema: bool = False,
    ) -> Callable[..., Any]:
        """
        Registers a GET route with all available parameters.
        """

        def decorator(handler: HandlerType) -> HandlerType:
            route = self.route_class(
                path=path,
                handler=handler,
                methods=["GET"],
                name=name,
                summary=summary,
                description=description,
                responses=responses,
                request_model=request_model,
                middlewares=middlewares,
                tags=tags,
                security=security,
                operation_id=operation_id,
                deprecated=deprecated,
                parameters=parameters,
                exclude_from_schema=exclude_from_schema,
            )
            self.add_route(route)
            return handler

        if handler is None:
            return decorator
        return decorator(handler)

    def post(
        self,
        path: str,
        handler: Optional[HandlerType] = None,
        name: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        responses: Optional[Dict[int, Any]] = None,
        request_model: Optional[Type[BaseModel]] = None,
        middlewares: List[Any] = [],
        tags: Optional[List[str]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
        operation_id: Optional[str] = None,
        deprecated: bool = False,
        parameters: List[Parameter] = [],
        exclude_from_schema: bool = False,
        **kwargs: Dict[str, Any],
    ) -> Callable[..., Any]:
        """
        Registers a POST route with all available parameters.
        """

        def decorator(handler: HandlerType) -> HandlerType:
            route = self.route_class(
                path=path,
                handler=handler,
                methods=["POST"],
                name=name,
                summary=summary,
                description=description,
                responses=responses,
                request_model=request_model,
                middlewares=middlewares,
                tags=tags,
                security=security,
                operation_id=operation_id,
                deprecated=deprecated,
                parameters=parameters,
                exclude_from_schema=exclude_from_schema,
            )
            self.add_route(route)
            return handler

        if handler is None:
            return decorator
        return decorator(handler)

    def delete(
        self,
        path: str,
        handler: Optional[HandlerType] = None,
        name: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        responses: Optional[Dict[int, Any]] = None,
        request_model: Optional[Type[BaseModel]] = None,
        middlewares: List[Any] = [],
        tags: Optional[List[str]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
        operation_id: Optional[str] = None,
        deprecated: bool = False,
        parameters: List[Parameter] = [],
        exclude_from_schema: bool = False,
        **kwargs: Dict[str, Any],
    ) -> Callable[..., Any]:
        """
        Registers a DELETE route with all available parameters.
        """

        def decorator(handler: HandlerType) -> HandlerType:
            route = self.route_class(
                path=path,
                handler=handler,
                methods=["DELETE"],
                name=name,
                summary=summary,
                description=description,
                responses=responses,
                request_model=request_model,
                middlewares=middlewares,
                tags=tags,
                security=security,
                operation_id=operation_id,
                deprecated=deprecated,
                parameters=parameters,
                exclude_from_schema=exclude_from_schema,
            )
            self.add_route(route)
            return handler

        if handler is None:
            return decorator
        return decorator(handler)

    def put(
        self,
        path: str,
        handler: Optional[HandlerType] = None,
        name: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        responses: Optional[Dict[int, Any]] = None,
        request_model: Optional[Type[BaseModel]] = None,
        middlewares: List[Any] = [],
        tags: Optional[List[str]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
        operation_id: Optional[str] = None,
        deprecated: bool = False,
        parameters: List[Parameter] = [],
        exclude_from_schema: bool = False,
        **kwargs: Dict[str, Any],
    ) -> Callable[..., Any]:
        """
        Registers a PUT route with all available parameters.
        """

        def decorator(handler: HandlerType) -> HandlerType:
            route = self.route_class(
                path=path,
                handler=handler,
                methods=["PUT"],
                name=name,
                summary=summary,
                description=description,
                responses=responses,
                request_model=request_model,
                middlewares=middlewares,
                tags=tags,
                security=security,
                operation_id=operation_id,
                deprecated=deprecated,
                parameters=parameters,
                exclude_from_schema=exclude_from_schema,
            )
            self.add_route(route)
            return handler

        if handler is None:
            return decorator
        return decorator(handler)

    def patch(
        self,
        path: str,
        handler: Optional[HandlerType] = None,
        name: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        responses: Optional[Dict[int, Any]] = None,
        request_model: Optional[Type[BaseModel]] = None,
        middlewares: List[Any] = [],
        tags: Optional[List[str]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
        operation_id: Optional[str] = None,
        deprecated: bool = False,
        parameters: List[Parameter] = [],
        exclude_from_schema: bool = False,
        **kwargs: Dict[str, Any],
    ) -> Callable[..., Any]:
        """
        Registers a PATCH route with all available parameters.
        """

        def decorator(handler: HandlerType) -> HandlerType:
            route = self.route_class(
                path=path,
                handler=handler,
                methods=["PATCH"],
                name=name,
                summary=summary,
                description=description,
                responses=responses,
                request_model=request_model,
                middlewares=middlewares,
                tags=tags,
                security=security,
                operation_id=operation_id,
                deprecated=deprecated,
                parameters=parameters,
                exclude_from_schema=exclude_from_schema,
            )
            self.add_route(route)
            return handler

        if handler is None:
            return decorator
        return decorator(handler)

    def options(
        self,
        path: str,
        handler: Optional[HandlerType] = None,
        name: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        responses: Optional[Dict[int, Any]] = None,
        request_model: Optional[Type[BaseModel]] = None,
        middlewares: List[Any] = [],
        tags: Optional[List[str]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
        operation_id: Optional[str] = None,
        deprecated: bool = False,
        parameters: List[Parameter] = [],
        exclude_from_schema: bool = False,
        **kwargs: Dict[str, Any],
    ) -> Callable[..., Any]:
        """
        Registers an OPTIONS route with all available parameters.
        """

        def decorator(handler: HandlerType) -> HandlerType:
            route = self.route_class(
                path=path,
                handler=handler,
                methods=["OPTIONS"],
                name=name,
                summary=summary,
                description=description,
                responses=responses,
                request_model=request_model,
                middlewares=middlewares,
                tags=tags,
                security=security,
                operation_id=operation_id,
                deprecated=deprecated,
                parameters=parameters,
                exclude_from_schema=exclude_from_schema,
            )
            self.add_route(route)
            return handler

        if handler is None:
            return decorator
        return decorator(handler)

    def head(
        self,
        path: str,
        handler: Optional[HandlerType] = None,
        name: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        responses: Optional[Dict[int, Any]] = None,
        request_model: Optional[Type[BaseModel]] = None,
        middlewares: List[Any] = [],
        tags: Optional[List[str]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
        operation_id: Optional[str] = None,
        deprecated: bool = False,
        parameters: List[Parameter] = [],
        exclude_from_schema: bool = False,
        **kwargs: Dict[str, Any],
    ) -> Callable[..., Any]:
        """
        Registers a HEAD route with all available parameters.
        """

        def decorator(handler: HandlerType) -> HandlerType:
            route = self.route_class(
                path=path,
                handler=handler,
                methods=["HEAD"],
                name=name,
                summary=summary,
                description=description,
                responses=responses,
                request_model=request_model,
                middlewares=middlewares,
                tags=tags,
                security=security,
                operation_id=operation_id,
                deprecated=deprecated,
                parameters=parameters,
                exclude_from_schema=exclude_from_schema,
            )
            self.add_route(route)
            return handler

        if handler is None:
            return decorator
        return decorator(handler)

    def route(
        self,
        path: str,
        methods: List[str] = allowed_methods_default,
        handler: Optional[HandlerType] = None,
        name: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        responses: Optional[Dict[int, Any]] = None,
        request_model: Optional[Type[BaseModel]] = None,
        middlewares: List[Any] = [],
        tags: Optional[List[str]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
        operation_id: Optional[str] = None,
        deprecated: bool = False,
        parameters: List[Parameter] = [],
        exclude_from_schema=False,
        **kwargs: Dict[str, Any],
    ) -> Callable[..., Any]:
        """
        Registers a route with all available parameters and customizable HTTP methods.
        """

        def decorator(handler: HandlerType) -> HandlerType:
            route = self.route_class(
                path=path,
                handler=handler,
                methods=methods,
                name=name,
                summary=summary,
                description=description,
                responses=responses,
                request_model=request_model,
                middlewares=middlewares,
                tags=tags,
                security=security,
                operation_id=operation_id,
                deprecated=deprecated,
                parameters=parameters,
                exclude_from_schema=exclude_from_schema,
            )
            self.add_route(route)
            return handler

        if handler is None:
            return decorator
        return decorator(handler)

    def url_for(self, _name: str, **path_params: Any) -> URLPath:
        """
        Generate a URL path for the route with the given name and parameters.

        Args:
            name: The name of the route.
            path_params: A dictionary of path parameters to substitute into the route's path.

        Returns:
            str: The generated URL path.

        Raises:
            ValueError: If the route name does not match or if required parameters are missing.
        """
        for route in self.routes:
            if route.name == _name:
                return route.url_path_for(_name, **path_params)
        raise ValueError(f"Route name '{_name}' not found in router.")

    def __repr__(self) -> str:
        return f"<Router prefix='{self.prefix}' routes={len(self.routes)}>"

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> Any:
        # return super().__call__(*args, **kwds)
        app = self.build_middleware_stack(self.app)
        await app(scope, receive, send)

    async def app(self, scope: Scope, receive: Receive, send: Send):
        url = get_route_path(scope)

        for mount_path, sub_app in self.sub_routers.items():
            if url.startswith(mount_path):
                scope["path"] = url[len(mount_path) :]
                await sub_app(scope, receive, send)
                return

        path_matched = False
        allowed_methods_: typing.Set[str] = set()
        for route in self.routes:
            match, matched_params, is_allowed = route.match(url, scope["method"])

            if match:
                path_matched = True
                if is_allowed:
                    route.handler = allowed_methods(route.methods)(route.handler)
                    scope["route_params"] = RouteParam(matched_params)
                    await route.handle(scope, receive, send)
                    return
                else:
                    allowed_methods_.update(route.methods)
        if path_matched:
            response = JSONResponse(
                content="Method not allowed",
                status_code=405,
                headers={"Allow": ", ".join(allowed_methods_)},
            )
            await response(scope, receive, send)
            return

        raise NotFoundException

    def mount_router(  # type:ignore
        self, app: "Router", path: typing.Optional[str] = None
    ) -> None:  # type:ignore
        """
        Mount an ASGI application (e.g., another Router) under a specific path prefix.

        Args:
            path: The path prefix under which the app will be mounted.
            app: The ASGI application (e.g., another Router) to mount.
        """

        if not path:
            path = app.prefix
        path = path.rstrip("/")

        if path == "":
            self.sub_routers[path] = app
            return
        if not path.startswith("/"):
            path = f"/{path}"

        if path in self.sub_routers.keys():
            raise ValueError("Router with prefix exists !")

        self.sub_routers[path] = app

    def get_all_routes(self) -> List[Routes]:
        """Returns a flat list of all HTTP routes in this router and all nested sub-routers"""
        all_routes: List[Routes] = []
        routers_to_process = [(self, "")]  # (router, current_prefix)

        while routers_to_process:
            current_router, current_prefix = routers_to_process.pop(0)

            # Add all routes from current router with prefix
            for route in current_router.routes:
                # Create a copy of the route with updated path
                new_route = copy.copy(route)
                new_route.raw_path = current_prefix + route.raw_path
                new_route.prefix = current_prefix
                all_routes.append(new_route)

            # Add all sub-routers to be processed with updated prefix
            for mount_path, sub_router in current_router.sub_routers.items():
                if isinstance(sub_router, Router):
                    new_prefix = current_prefix + mount_path
                    routers_to_process.append((sub_router, new_prefix))

        return all_routes


class WebsocketRoutes:
    def __init__(
        self,
        path: str,
        handler: WsHandlerType,
        middlewares: typing.List[WsMiddlewareType] = [],
    ):
        assert callable(handler), "Route handler must be callable"
        self.raw_path = path
        self.handler: WsHandlerType = handler
        self.middlewares = middlewares
        self.route_info = RouteBuilder.create_pattern(path)
        self.pattern = self.route_info.pattern
        self.param_names = self.route_info.param_names
        self.route_type = self.route_info.route_type
        self.router_middleware = None

    def match(self, path: str) -> typing.Tuple[Any, Any]:
        """
        Match a path against this route's pattern and return captured parameters.

        Args:
            path: The URL path to match.

        Returns:
            Optional[Dict[str, Any]]: A dictionary of captured parameters if the path matches,
            otherwise None.
        """
        match = self.pattern.match(path)
        if match:
            matched_params = match.groupdict()
            for key, value in matched_params.items():
                matched_params[key] = self.route_info.convertor[
                    key
                ].convert(  # type:ignore
                    value
                )  # type:ignore
            return match, matched_params
        return None, None

    async def handle(self, websocket: WebSocket) -> None:
        """
        Handles the WebSocket connection by calling the route's handler.

        Args:
            websocket: The WebSocket connection.
            params: The extracted route parameters.
        """
        await self.handler(websocket)

    def __repr__(self) -> str:
        return f"<WSRoute {self.raw_path}>"

    async def execute_middleware_stack(
        self, ws: "WebsocketRoutes", **kwargs: Dict[str, Any]
    ) -> Union[WsMiddlewareType, None]:
        """
        Executes WebSocket middleware stack after route matching.
        """
        middleware_list: List[WsMiddlewareType] = getattr(self, "router_middleware") or []  # type: ignore

        stack: List[WsMiddlewareType] = middleware_list.copy()
        index = -1

        async def next_middleware() -> WsMiddlewareType:
            nonlocal index
            index += 1
            if index < len(stack):  # type: ignore
                middleware: List[MiddlewareType] = stack[index]  # type: ignore
                return await middleware(ws, next_middleware, **kwargs)  # type: ignore
            else:
                # No more middleware to process
                return None  # type: ignore

        return await next_middleware()


class WSRouter(BaseRouter):
    def __init__(
        self, prefix: Optional[str] = None, middleware: Optional[List[Any]] = []
    ):
        self.prefix = prefix or ""
        self.routes: List[WebsocketRoutes] = []
        self.middlewares: List[Callable[[ASGIApp], ASGIApp]] = []
        self.sub_routers: Dict[str, ASGIApp] = {}
        if self.prefix and not self.prefix.startswith("/"):
            warnings.warn("WSRouter prefix should start with '/'")
            self.prefix = f"/{self.prefix}"

    def add_ws_route(
        self,
        route: Annotated[
            WebsocketRoutes,
            Doc("An instance of the Routes class representing a WebSocket route."),
        ],
    ) -> None:
        """
        Adds a WebSocket route to the application.

        This method registers a WebSocket route, allowing the application to handle WebSocket connections.

        Args:
            route (Routes): The WebSocket route configuration.

        Returns:
            None

        Example:
            ```python
            route = Routes("/ws/chat", chat_handler)
            app.add_ws_route(route)
            ```
        """
        self.routes.append(route)

    def add_ws_middleware(self, middleware: type[ASGIApp]) -> None:  # type: ignore[override]
        """Add middleware to the WebSocket router"""
        self.middlewares.insert(0, middleware)  # type: ignore

    def ws_route(
        self,
        path: Annotated[
            str, Doc("The WebSocket route path. Must be a valid URL pattern.")
        ],
        middlewares: Annotated[
            List[WsMiddlewareType],
            Doc("List of middleware to be executes before the router handler"),
        ] = [],
    ) -> Union[WsHandlerType, Any]:
        """
        Registers a WebSocket route.

        This decorator is used to define WebSocket routes in the application, allowing handlers
        to manage WebSocket connections. When a WebSocket client connects to the given path,
        the specified handler function will be executed.

        Returns:
            Callable: The original WebSocket handler function.

        Example:
            ```python

            @app.ws_route("/ws/chat")
            async def chat_handler(websocket):
                await websocket.accept()
                while True:
                    message = await websocket.receive_text()
                    await websocket.send_text(f"Echo: {message}")
            ```
        """

        def decorator(handler: WsHandlerType) -> WsHandlerType:
            self.add_ws_route(WebsocketRoutes(path, handler, middlewares=middlewares))
            return handler

        return decorator

    def build_middleware_stack(  # type:ignore
        self, scope: Scope, receive: Receive, send: Send
    ) -> ASGIApp:  # type:ignore
        app = self.app
        for mdw in reversed(self.middlewares):
            app = mdw(app)  # type:ignore[assignment]
        return app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "websocket":
            return
        app = self.build_middleware_stack(scope, receive, send)
        app = WebSocketErrorMiddleware(app)
        await app(scope, receive, send)

    async def app(self, scope: Scope, receive: Receive, send: Send) -> None:

        url = get_route_path(scope)
        for mount_path, sub_app in self.sub_routers.items():
            if url.startswith(mount_path):
                scope["path"] = url[len(mount_path) :]
                await sub_app(scope, receive, send)
                return
        for route in self.routes:
            match, params = route.match(url)
            if match:
                websocket = WebSocket(scope, receive, send)
                scope["route_params"] = params
                await route.handle(websocket)
                return
        await send({"type": "websocket.close", "code": 404})

    def wrap_asgi(
        self,
        middleware_cls: Annotated[
            Callable[[ASGIApp], Any],
            Doc(
                "An ASGI middleware class or callable that takes an app as its first argument and returns an ASGI app"
            ),
        ],
    ) -> None:
        """
        Wraps the entire application with an ASGI middleware.

        This method allows adding middleware at the ASGI level, which intercepts all requests
        (HTTP, WebSocket, and Lifespan) before they reach the application.

        Args:
            middleware_cls: An ASGI middleware class or callable that follows the ASGI interface
            *args: Additional positional arguments to pass to the middleware
            **kwargs: Additional keyword arguments to pass to the middleware

        Returns:
            NexiosApp: The application instance for method chaining


        """
        self.app = middleware_cls(self.app)

    def mount_router(  # type:ignore
        self, app: "WSRouter", path: typing.Optional[str] = None
    ) -> None:  # type:ignore
        """
        Mount an ASGI application (e.g., another Router) under a specific path prefix.

        Args:
            path: The path prefix under which the app will be mounted.
            app: The ASGI application (e.g., another Router) to mount.
        """

        if not path:
            path = app.prefix
        path = path.rstrip("/")

        if path == "":
            self.sub_routers[path] = app
            return
        if not path.startswith("/"):
            path = f"/{path}"

        self.sub_routers[path] = app

    def __repr__(self) -> str:
        return f"<WSRouter prefix='{self.prefix}' routes={len(self.routes)}>"
