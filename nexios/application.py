from typing import Any, Callable, List, Type, Union, Type
from .routing import Router, WSRouter, WebsocketRoutes, Routes
import typing
from .exception_handler import ExceptionMiddleware
from typing_extensions import Doc, Annotated  # type:ignore
from nexios.config import DEFAULT_CONFIG, MakeConfig
from typing import Awaitable, Optional, AsyncIterator
from nexios.logging import create_logger
from nexios.middlewares.core import BaseMiddleware
from nexios.middlewares.core import Middleware
from nexios.middlewares.errors.server_error_handler import (
    ServerErrorMiddleware,
    ServerErrHandlerType,
)
from nexios.structs import URLPath
from pydantic import BaseModel
from nexios.openapi.models import Parameter, Path, Schema
from .types import MiddlewareType, Scope, Send, Receive, Message, HandlerType, ASGIApp
from nexios.openapi.config import OpenAPIConfig
from nexios.openapi.models import HTTPBearer
from nexios.openapi._builder import APIDocumentation

allowed_methods_default = ["get", "post", "delete", "put", "patch", "options"]

from typing import Dict, Any

AppType = typing.TypeVar("AppType", bound="NexiosApp")


logger = create_logger("nexios")


class NexiosApp(object):
    def __init__(
        self,
        config: Annotated[
            Optional[MakeConfig],
            Doc(
                """
                    This subclass is derived from the MakeConfig class and is responsible for managing configurations within the Nexios framework. It takes arguments in the form of dictionaries, allowing for structured and flexible configuration handling. By using dictionaries, this subclass makes it easy to pass multiple configuration values at once, reducing complexity and improving maintainability.

                    One of the key advantages of this approach is its ability to dynamically update and modify settings without requiring changes to the core codebase. This is particularly useful in environments where configurations need to be frequently adjusted, such as database settings, API credentials, or feature flags. The subclass can also validate the provided configuration data, ensuring that incorrect or missing values are handled properly.

                    Additionally, this design allows for merging and overriding configurations, making it adaptable for various use cases. Whether used for small projects or large-scale applications, this subclass ensures that configuration management remains efficient and scalable. By extending MakeConfig, it leverages existing functionality while adding new capabilities tailored to Nexios. This makes it an essential component for maintaining structured and well-organized application settings.
                    """
            ),
        ] = DEFAULT_CONFIG,
        middlewares: Annotated[
            List[Middleware],
            Doc(
                "A list of middlewares, where each middleware is either a class inherited from BaseMiddleware or an asynchronous callable function that accepts request, response, and callnext"
            ),
        ] = [],
        server_error_handler: Annotated[
            Optional[ServerErrHandlerType],
            Doc(
                """
                        A function in Nexios responsible for handling server-side exceptions by logging errors, reporting issues, or initiating recovery mechanisms. It prevents crashes by intercepting unexpected failures, ensuring the application remains stable and operational. This function provides a structured approach to error management, allowing developers to define custom handling strategies such as retrying failed requests, sending alerts, or gracefully degrading functionality. By centralizing error processing, it improves maintainability and observability, making debugging and monitoring more efficient. Additionally, it ensures that critical failures do not disrupt the entire system, allowing services to continue running while appropriately managing faults and failures."""
            ),
        ] = None,
        lifespan: Optional[Callable[["NexiosApp"], AsyncIterator[None]]] = None,
    ):

        self.config = config or DEFAULT_CONFIG
        self.server_error_handler = None
        self.ws_router = WSRouter()
        self.ws_routes: List[WebsocketRoutes] = []
        self.http_middlewares: List[Middleware] = middlewares or []
        self.ws_middlewares: List[ASGIApp] = []
        self.startup_handlers: List[Callable[[], Awaitable[None]]] = []
        self.shutdown_handlers: List[Callable[[], Awaitable[None]]] = []
        self.exceptions_handler: Any[ExceptionMiddleware, None] = (
            server_error_handler or ExceptionMiddleware()
        )

        self.app = Router()
        self.router = self.app
        self.route = self.router.route
        self.lifespan_context: Optional[
            Callable[["NexiosApp"], AsyncIterator[None]]
        ] = lifespan
        self.lifespan_context: Optional[
            Callable[["NexiosApp"], AsyncIterator[None]]
        ] = lifespan

        openapi_config: Dict[str, Any] = self.config.to_dict().get(
            "openapi", {}
        )  # type:ignore
        self.openapi_config = OpenAPIConfig(
            title=openapi_config.get("title", "Nexios API"),
            version=openapi_config.get("version", "1.0.0"),
            description=openapi_config.get(
                "description", "Automatically generated API documentation"
            ),
            license=openapi_config.get("license"),
            contact=openapi_config.get("contact"),
        )

        self.openapi_config.add_security_scheme(
            "bearerAuth", HTTPBearer(type="http", scheme="bearer", bearerFormat="JWT")
        )

        self.docs = APIDocumentation(
            app=self,
            config=self.openapi_config,
        )

    def on_startup(self, handler: Callable[[], Awaitable[None]]) -> None:
        """
        Registers a startup handler that executes when the application starts.

        This method allows you to define functions that will be executed before
        the application begins handling requests. It is useful for initializing
        resources such as database connections, loading configuration settings,
        or preparing caches.

        The provided function must be asynchronous (`async def`) since it
        will be awaited during the startup phase.

        Args:
            handler (Callable): An asynchronous function to be executed at startup.

        Returns:
            Callable: The same handler function, allowing it to be used as a decorator.

        Example:
            ```python

            @app.on_startup
            async def connect_to_db():
                global db
                db = await Database.connect("postgres://user:password@localhost:5432/mydb")
                print("Database connection established.")

            @app.on_startup
            async def cache_warmup():
                global cache
                cache = await load_initial_cache()
                print("Cache warmed up and ready.")
            ```

        In this example:
        - `connect_to_db` establishes a database connection before the app starts.
        - `cache_warmup` preloads data into a cache for faster access.

        These functions will be executed in the order they are registered when the
        application starts.
        """
        self.startup_handlers.append(handler)

    def on_shutdown(self, handler: Callable[[], Awaitable[None]]) -> None:
        """
        Registers a shutdown handler that executes when the application is shutting down.

        This method allows you to define functions that will be executed when the
        application is stopping. It is useful for cleaning up resources such as
        closing database connections, saving application state, or gracefully
        terminating background tasks.

        The provided function must be asynchronous (`async def`) since it will be
        awaited during the shutdown phase.

        Args:
            handler (Callable): An asynchronous function to be executed during shutdown.

        Returns:
            Callable: The same handler function, allowing it to be used as a decorator.

        Example:
            ```python
            app = NexioApp()

            @app.on_shutdown
            async def disconnect_db():
                global db
                await db.disconnect()
                print("Database connection closed.")

            @app.on_shutdown
            async def clear_cache():
                global cache
                await cache.clear()
                print("Cache cleared before shutdown.")
            ```

        In this example:
        - `disconnect_db` ensures that the database connection is properly closed.
        - `clear_cache` removes cached data to free up memory before the app stops.

        These functions will be executed in the order they are registered when the
        application is shutting down.
        """
        self.shutdown_handlers.append(handler)

    async def _startup(self) -> None:
        """Execute all startup handlers sequentially"""
        self._setup_openapi()
        for handler in self.startup_handlers:
            try:
                await handler()
            except Exception as e:
                raise e

    async def _shutdown(self) -> None:
        """Execute all shutdown handlers sequentially with error handling"""
        for handler in self.shutdown_handlers:
            try:
                await handler()
            except Exception as e:
                raise e

    async def handle_lifespan(self, receive: Receive, send: Send) -> None:
        """Handle ASGI lifespan protocol events."""
        try:
            while True:
                message: Message = await receive()
                if message["type"] == "lifespan.startup":
                    try:
                        if self.lifespan_context:
                            # If a lifespan context manager is provided, use it
                            self.lifespan_manager: Any = self.lifespan_context(self)
                            await self.lifespan_manager.__aenter__()
                        else:
                            # Otherwise, fall back to the default startup handlers
                            await self._startup()
                        await send({"type": "lifespan.startup.complete"})
                    except Exception as e:
                        await send(
                            {"type": "lifespan.startup.failed", "message": str(e)}
                        )
                        return

                elif message["type"] == "lifespan.shutdown":
                    try:
                        if self.lifespan_context:
                            # If a lifespan context manager is provided, use it
                            await self.lifespan_manager.__aexit__(None, None, None)
                        else:
                            # Otherwise, fall back to the default shutdown handlers
                            await self._shutdown()
                        await send({"type": "lifespan.shutdown.complete"})
                        return
                    except Exception as e:
                        await send(
                            {"type": "lifespan.shutdown.failed", "message": str(e)}
                        )
                        return

        except Exception as e:
            if message["type"].startswith("lifespan.startup"):  # type: ignore
                await send({"type": "lifespan.startup.failed", "message": str(e)})
            else:
                await send({"type": "lifespan.shutdown.failed", "message": str(e)})

        except Exception as e:  # type:ignore
            if message["type"].startswith("lifespan.startup"):  # type: ignore
                await send({"type": "lifespan.startup.failed", "message": str(e)})
            else:
                await send({"type": "lifespan.shutdown.failed", "message": str(e)})

    def _setup_openapi(self):
        """Set up automatic OpenAPI documentation"""
        docs = self.docs

        for route in self.get_all_routes():
            if route.exlude_from_schema:
                continue
            for method in route.methods:

                parameters = [
                    Path(name=x, schema=Schema(type="string"), schema_=None) # type: ignore
                    for x in route.param_names
                ]  
                if route.parameters.__len__() > 0:
                    parameters.extend(parameters)
                docs.document_endpoint(
                    path=route.raw_path,
                    method=method,
                    tags=route.tags,
                    security=route.security,
                    summary=route.summary or "",
                    description=route.description,
                    request_body=route.request_model,
                    parameters=parameters,  # type:ignore
                    deprecated=route.deprecated,
                    operation_id=route.operation_id,
                    responses=route.responses,
                )(route.handler)

    def add_middleware(
        self,
        middleware: Annotated[
            MiddlewareType,
            Doc(
                "A callable middleware function that processes requests and responses."
            ),
        ],
    ) -> None:
        """
        Adds middleware to the application.

        Middleware functions are executed in the request-response lifecycle, allowing
        modifications to requests before they reach the route handler and responses
        before they are sent back to the client.

        Args:
            middleware (MiddlewareType): A callable that takes a `Request`, `Response`,
            and a `Callable` (next middleware or handler) and returns a `Response`.

        Returns:
            None

        Example:
            ```python
            def logging_middleware(request: Request, response: Response, next_call: Callable) -> Response:
                print(f"Request received: {request.method} {request.url}")
                return next_call(request, response)

            app.add_middleware(logging_middleware)
            ```
        """

        self.http_middlewares.insert(
            0, Middleware(BaseMiddleware, dispatch=middleware)  # type:ignore
        )

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
        self.ws_router.add_ws_route(route)

    def ws_route(self, route: str):

        return self.ws_router.ws_route(route)

    def mount_router(self, router: Router, path: typing.Optional[str] = None):
        """
        Mounts a router and all its routes to the application.

        This method allows integrating another `Router` instance, registering all its
        defined routes into the current application. It is useful for modularizing routes
        and organizing large applications.

        Args:
            router (Router): The `Router` instance whose routes will be added.

        Returns:
            None

        Example:
            ```python
            user_router = Router()

            @user_router.route("/users", methods=["GET"])
            def get_users(request, response):
                 response.json({"users": ["Alice", "Bob"]})

            app.mount_router(user_router)  # Mounts the user routes into the main app
            ```
        """
        self.router.mount_router(router, path=path)

    def mount_ws_router(
        self,
        router: Annotated[
            "WSRouter",
            Doc("An instance of Router containing multiple routes to be mounted."),
        ],
    ) -> None:
        """
        Mounts a router and all its routes to the application.

        This method allows integrating another `Router` instance, registering all its
        defined routes into the current application. It is useful for modularizing routes
        and organizing large applications.

        Args:
            router (Router): The `Router` instance whose routes will be added.

        Returns:
            None

        Example:
            ```python
            chat_router = WSRouter()

            @chat_router.ws("/users")
            def get_users(ws):
                ...

            app.mount_ws_router(chat_router)  # Mounts the user routes into the main app
            ```
        """
        self.ws_router.mount_router(router)

    async def handle_websocket(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        app = self.ws_router
        for mdw in reversed(self.ws_middlewares):
            app = mdw(app)  # type:ignore
        await app(scope, receive, send)

    def add_ws_middleware(
        self,
        middleware: Annotated[
            ASGIApp,
            Doc(
                "A callable function that intercepts and processes WebSocket connections."
            ),
        ],
    ) -> None:
        """
        Adds a WebSocket middleware to the application.

        WebSocket middleware functions allow pre-processing of WebSocket requests before they
        reach their final handler. Middleware can be used for authentication, logging, or
        modifying the WebSocket request/response.

        Args:
            middleware (Callable): A callable function that handles WebSocket connections.

        Returns:
            None

        Example:
            ```python
            def ws_auth_middleware(ws, next_handler):
                if not ws.headers.get("Authorization"):
                    ...
                return next_handler(ws)

            app.add_ws_middleware(ws_auth_middleware)
            ```
        """
        self.ws_middlewares.append(middleware)

    def handle_http_request(self) -> Router:
        app = self.app
        middleware = (
            [
                Middleware(
                    BaseMiddleware,
                    dispatch=ServerErrorMiddleware(handler=self.server_error_handler),
                )
            ]
            + self.http_middlewares
            + [Middleware(BaseMiddleware, dispatch=self.exceptions_handler)]
        )
        for cls, args, kwargs in reversed(middleware):
            app = cls(app, *args, **kwargs)
        return app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI application callable"""
        scope["app"] = self
        if scope["type"] == "lifespan":
            await self.handle_lifespan(receive, send)
        elif scope["type"] == "http":
            await self.handle_http_request()(scope, receive, send)

        else:

            await self.handle_websocket(scope, receive, send)

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
        **kwargs: Dict[str, Any]
    ) -> Callable[..., Any]:
        """
        Registers a GET route with all available parameters.
        """

        return self.route(
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
            **kwargs
        )

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
        **kwargs: Dict[str, Any]
    ) -> Callable[..., Any]:
        """
        Registers a POST route with all available parameters.
        """

        return self.route(
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
            **kwargs
        )

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
        **kwargs: Dict[str, Any]
    ) -> Callable[..., Any]:
        """
        Registers a DELETE route with all available parameters.
        """

        return self.route(
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
            **kwargs
        )

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
        **kwargs: Dict[str, Any]
    ) -> Callable[..., Any]:
        """
        Registers a PUT route with all available parameters.
        """

        return self.route(
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
            **kwargs
        )

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
        **kwargs: Dict[str, Any]
    ) -> Callable[..., Any]:
        """
        Registers a PATCH route with all available parameters.
        """
        return self.route(
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
            **kwargs
        )

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
        **kwargs: Dict[str, Any]
    ) -> Callable[..., Any]:
        """
        Registers an OPTIONS route with all available parameters.
        """
        return self.route(
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
            **kwargs
        )

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
        **kwargs: Dict[str, Any]
    ) -> Callable[..., Any]:
        """
        Registers a HEAD route with all available parameters.
        """

        return self.route(
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
            **kwargs
        )

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

        self.router.add_route(route)

    def add_exception_handler(
        self,
        exc_class_or_status_code: Union[typing.Type[Exception], int],
        handler: HandlerType,
    ) -> None:
        self.exceptions_handler.add_exception_handler(exc_class_or_status_code, handler)

    def url_for(self, _name: str, **path_params: Any) -> URLPath:
        return self.router.url_for(_name, **path_params)

    def wrap_asgi(
        self,
        middleware_cls: Annotated[
            Callable[[ASGIApp], Any],
            Doc(
                "An ASGI middleware class or callable that takes an app as its first argument and returns an ASGI app"
            ),
        ],
        **kwargs: Dict[str, Any]
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
        self.app = middleware_cls(self.app, **kwargs)

    def get_all_routes(self) -> List[Routes]:
        """
        Returns all routes registered in the application.

        This method retrieves a list of all HTTP and WebSocket routes defined in the application.

        Returns:
            List[Routes]: A list of all registered routes.

        Example:
            ```python
            routes = app.get_all_routes()
            for route in routes:
                print(route.path, route.methods)
            ```
        """
        return self.router.get_all_routes()
