from typing import Any, List, Optional, Pattern,Dict,TypeVar,Tuple,Callable,Union
from dataclasses import dataclass
import re
import warnings
from enum import Enum
from nexios.types import MiddlewareType,WsMiddlewareType,HandlerType,WsHandlerType
from nexios.decorators import allowed_methods
from typing_extensions import Doc,Annotated #type: ignore
from nexios.structs import URLPath
from nexios.http import Request,Response
T = TypeVar("T")
allowed_methods_default = ['get','post','delete','put','patch','options']


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

class RouteBuilder:
    """Handles route pattern creation and processing"""
    
    @staticmethod
    def create_pattern(path: str) -> RoutePattern:
        """Create a route pattern from a path string"""
        param_names :List[str] = []
        
        if path.startswith("^"):
            return RoutePattern(
                pattern=re.compile(path),
                raw_path=path,
                param_names=re.findall(r'\?P<(\w+)>', path),
                route_type=RouteType.REGEX
            )
            
        if "*" in path:
            wildcard_pattern = path.replace("*", ".*?")
            return RoutePattern(
                pattern=re.compile(f"^{wildcard_pattern}$"),
                raw_path=path,
                param_names=[],
                route_type=RouteType.WILDCARD
            )
            
        processed_path = path
        

        if path.startswith("^") or path.endswith("$"):
            return RoutePattern(
                pattern=re.compile(path),
                raw_path=path,
                param_names=re.findall(r'\?P<(\w+)>', path),
                route_type=RouteType.REGEX
            )
        
        param_matches = re.finditer(r"{(\w+)(?::([^}]+))?}", path)
        for match in param_matches:
            param_name = match.group(1)
            constraint = match.group(2) or "[^/]+"
            param_names.append(param_name)
            processed_path = processed_path.replace(
                match.group(0),
                f"(?P<{param_name}>{constraint})"
            )
            
        return RoutePattern(
            pattern=re.compile(f"^{processed_path}$"),
            raw_path=path,
            param_names=param_names,
            route_type=RouteType.PATH
        )

class BaseRouter:
    def add_route(self, route: 'Routes') -> None:
        raise NotImplementedError("Not implemented")
    
    def get_routes(self): #type:ignore
        raise NotImplementedError("Not implemented")
    
    def add_middleware(self, middleware: MiddlewareType) -> Any: #type:ignore
        raise NotImplementedError("Not implemented")

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
            Doc("""
            URL path pattern for the endpoint. Supports dynamic parameters using curly brace syntax.
            Examples:
            - '/users' (static path)
            - '/posts/{id}' (path parameter)
            - '/files/{filepath:.*}' (regex-matched path parameter)
            """)
        ],
        handler: Annotated[
            Optional[HandlerType], 
            Doc("""
            Callable responsible for processing requests to this endpoint. Can be:
            - A regular function
            - An async function
            - A class method
            - Any object implementing __call__

            The handler should accept a request object and return a response object.
            Example: def user_handler(request: Request) -> Response: ...
            """)
        ],
        methods: Annotated[
            Optional[List[str]], 
            Doc("""
            HTTP methods allowed for this endpoint. Common methods include:
            - GET: Retrieve resources
            - POST: Create resources
            - PUT: Update resources
            - DELETE: Remove resources
            - PATCH: Partial updates

            Defaults to ['GET'] if not specified. Use uppercase method names.
            """)
        ] = None,
        name :Optional[str] = None,
       
        **kwargs :Dict[str,Any]
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
        
        self.raw_path = path
        self.handler = handler
        self.methods = methods or allowed_methods_default
        self.name = name
       
        
        self.route_info = RouteBuilder.create_pattern(path)
        self.pattern: Pattern[str] = self.route_info.pattern
        self.param_names = self.route_info.param_names
        self.route_type = self.route_info.route_type
        self.router_middleware = None
        

    def match(self, path: str) -> re.Match[str] | None:
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
            return match
        return None
    
    def url_path_for(self, name: str, **path_params: Any) -> URLPath:
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
        if name != self.name:
            raise ValueError(f"Route name '{name}' does not match the current route name '{self.name}'.")

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
            path = path.replace(f"{{{param_name}}}", param_value)

        return URLPath(path = path,protocol="http")
    
    
    
    async def handle(self, request: Request, response: Response) -> Any:
        """
        Process an incoming request using the route's handler.

        Args:
            request: The incoming HTTP request object.
            response: The outgoing HTTP response object.

        Returns:
            Response: The processed HTTP response object.
        """
       
        
        return await self.handler(request, response)
            
           
  
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
    def __init__(self, prefix: Optional[str] = None, routes :Optional[List[Routes]] = None):
        self.prefix = prefix or ""
        self.prefix.rstrip("/")
        self.routes: List[Routes] =  list(routes) if routes else []
        self.middlewares: List[MiddlewareType] = []
        
        if self.prefix and not self.prefix.startswith("/"):
            warnings.warn("Router prefix should start with '/'")
            self.prefix = f"/{self.prefix}"
    
    def add_route(
        self, 
        route: Annotated[Routes, 
                         Doc("An instance of the Routes class representing an HTTP route.")]
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
            
        route.raw_path = f"{self.prefix}{route.raw_path}"
    
        route.route_info = RouteBuilder.create_pattern(route.raw_path)
        route.pattern = route.route_info.pattern
        route.param_names = route.route_info.param_names
        route.route_type = route.route_info.route_type
        
        self.routes.append(route)
    
    def add_middleware(self, middleware: MiddlewareType) -> None:
        """Add middleware to the router"""
        if callable(middleware):
            self.middlewares.append(middleware)
    


    def mount_router(self, router :"Router") -> None:
        """Mount a router and all its routes to the application"""
        self.routes.extend(router.routes)
        self.middlewares.extend(router.middlewares)

    def get(
        self,
        path: Annotated[
            str,
            Doc("The URL path pattern for the endpoint. Supports dynamic parameters using curly brace syntax.")
        ],
        name: Annotated[
            Optional[str],
            Doc("A unique name for the route.")
        ] = None,
       
        **kwargs: Annotated[
            Dict[str, Any],
            Doc("Additional arguments to pass to the Routes class.")
        ]
    ) -> Callable[..., Any]:
        """
        Registers a GET route.

        This decorator allows you to define an endpoint that handles HTTP GET requests. 
        GET requests are typically used for retrieving resources.

        Args:
            route (Routes): The route definition, including path and handler function.
            validator (Callable, optional): A function to validate the request data before passing it to the handler.

        Returns:
            Callable: The decorated handler function.

        Example:
            ```python
            @app.get("/users")
            async def get_users(request,response):
                return response.json({"users": ["Alice", "Bob"]})
            ```
        """
        return self.route(path=f"{path}", 
                           methods=["GET"], 
                           name=name,
                            **kwargs)


    def post(
        self,
        path: Annotated[
            str,
            Doc("The URL path pattern for the endpoint. Supports dynamic parameters using curly brace syntax.")
        ],
        name: Annotated[
            Optional[str],
            Doc("A unique name for the route.")
        ] = None,
       
        **kwargs: Annotated[
            Dict[str, Any],
            Doc("Additional arguments to pass to the Routes class.")
        ]
    ) -> Callable[..., Any]:
        """
        Registers a POST route.

        This decorator is used to define an endpoint that handles HTTP POST requests, 
        typically for creating resources.

        Args:
            route (Routes): The route definition, including path and handler function.
            validator (Callable, optional): A function to validate the request data before passing it to the handler.

        Returns:
            Callable: The decorated handler function.

        Example:
            ```python
            @app.post("/users")
            async def create_user(request,response):
                return response.json({"message": "User created"})
            ```
        """
        return self.route(path=f"{path}", 
                           methods=["POST"], 
                           name=name,
                            **kwargs)


    def delete(
        self,
        path: Annotated[
            str,
            Doc("The URL path pattern for the endpoint. Supports dynamic parameters using curly brace syntax.")
        ],
        name: Annotated[
            Optional[str],
            Doc("A unique name for the route.")
        ] = None,
       
        **kwargs: Annotated[
            Dict[str, Any],
            Doc("Additional arguments to pass to the Routes class.")
        ]
    ) -> Callable[..., Any]:
        """
        Registers a DELETE route.

        This decorator allows defining an endpoint that handles HTTP DELETE requests, 
        typically for deleting resources.

        Args:
            route (Routes): The route definition, including path and handler function.
            validator (Callable, optional): A function to validate the request data before passing it to the handler.

        Returns:
            Callable: The decorated handler function.

        Example:
            ```python
            @app.delete("/users/{user_id}")
            def delete_user(request, response):
                user_id = request.path_params.user_id
                return responsejson({"message": f"User {user_id} deleted"})
            ```
        """
        return self.route(path=f"{path}", 
                           methods=["DELETE"],                      
                           name=name,
                            **kwargs)


    def put(
        self,
        path: Annotated[
            str,
            Doc("The URL path pattern for the endpoint. Supports dynamic parameters using curly brace syntax.")
        ],
        name: Annotated[
            Optional[str],
            Doc("A unique name for the route.")
        ] = None,
       
        **kwargs: Annotated[
            Dict[str, Any],
            Doc("Additional arguments to pass to the Routes class.")
        ]
    ) -> Callable[..., Any]:
        """
        Registers a PUT route.

        This decorator defines an endpoint that handles HTTP PUT requests, 
        typically for updating or replacing a resource.

        Args:
            route (Routes): The route definition, including path and handler function.
            validator (Callable, optional): A function to validate the request data before passing it to the handler.

        Returns:
            Callable: The decorated handler function.

        Example:
            ```python
            @app.delete("/users/{user_id}")
            def delete_user(request, response):
                user_id = request.path_params.user_id
                return responsejson({"message": f"User {user_id} updated"})
        """
        return self.route(path=f"{path}", 
                           methods=["PUT"], 
                           name=name,
                            **kwargs)

    def patch(
        self,
        path: Annotated[
            str,
            Doc("The URL path pattern for the endpoint. Supports dynamic parameters using curly brace syntax.")
        ],
        name: Annotated[
            Optional[str],
            Doc("A unique name for the route.")
        ] = None,
       
        **kwargs: Annotated[
            Dict[str, Any],
            Doc("Additional arguments to pass to the Routes class.")
        ]
    ) -> Callable[..., Any]:
        """
        Registers a PATCH route.

        This decorator defines an endpoint that handles HTTP PATCH requests, 
        which are used to apply partial modifications to a resource.

        Args:
            route (Routes): The route definition, including path and handler function.
            validator (Callable, optional): A function to validate the request data before passing it to the handler.

        Returns:
            Callable: The decorated handler function.

        Example:
            ```python
            @app.patch("/users/{user_id}")
            def partial_update_user(request, response):
                user_id = request.path_params.user_id
            
                return respoonse.json({"message": f"User {user_id} partially updated"})
            ```
        """
        return self.route(path=f"{path}", 
                           methods=["PATCH"], 
                           name=name,
                            **kwargs)


    def options(
        self,
        path: Annotated[
            str,
            Doc("The URL path pattern for the endpoint. Supports dynamic parameters using curly brace syntax.")
        ],
        handler: Annotated[
            Optional[HandlerType],
            Doc("Callable responsible for processing requests to this endpoint.")
        ] = None,
        name: Annotated[
            Optional[str],
            Doc("A unique name for the route.")
        ] = None,
       
        **kwargs: Annotated[
            Dict[str, Any],
            Doc("Additional arguments to pass to the Routes class.")
        ]
    ) -> Callable[..., Any]:
        """
        Registers an OPTIONS route.

        This decorator defines an endpoint that handles HTTP OPTIONS requests, 
        which are used to describe the communication options for the target resource. 
        OPTIONS requests are commonly used in CORS (Cross-Origin Resource Sharing) 
        to check allowed methods, headers, and authentication rules.

        Args:
            route (Routes): The route definition, including path and handler function.
            validator (Callable, optional): A function to validate the request data before passing it to the handler.

        Returns:
            Callable: The decorated handler function.

        Example:
            ```python
            @app.options("/users")
            def options_users(request):
                return response.json({
                    "Allow": "GET, POST, DELETE, OPTIONS"
                })
            ```
        """
        return self.route(path=f"{path}", 
                           methods=["OPTIONS"], 
                           name=name,
                            **kwargs)



    def head(
        self,
        path: Annotated[
            str,
            Doc("The URL path pattern for the endpoint. Supports dynamic parameters using curly brace syntax.")
        ],
        handler: Annotated[
            Optional[HandlerType],
            Doc("Callable responsible for processing requests to this endpoint.")
        ] = None,
        name: Annotated[
            Optional[str],
            Doc("A unique name for the route.")
        ] = None,
       
        **kwargs: Annotated[
            Dict[str, Any],
            Doc("Additional arguments to pass to the Routes class.")
        ]
    ) -> Callable[..., Any]:
        
         return self.route(path=f"{path}", 
                           methods=["HEAD"], 
                           name=name,
                            **kwargs)
    
    def route(
        self,
        path: Annotated[
            str,
            Doc("The URL path pattern for the endpoint. Supports dynamic parameters using curly brace syntax.")
        ],
        methods: Annotated[
            List[str],
            Doc(f"HTTP methods allowed for this endpoint. Defaults to {allowed_methods_default}.")
        ] = allowed_methods_default,
        name: Annotated[
            Optional[str],
            Doc("A unique name for the route.")
        ] = None,
       
        **kwargs: Annotated[
            Dict[str, Any],
            Doc("Additional arguments to pass to the Routes class.")
        ]
    ) -> Callable[...,Any]:
        """
        Registers a route with the specified HTTP methods and an optional validator.

        This decorator allows developers to define HTTP routes for the application by specifying
        the URL path, allowed methods, and an optional parameter validator. It ensures that the 
        handler only responds to the defined HTTP methods.

       

        Example:
            ```python

            @app.route("/users", methods=["GET"])
            async def get_users(request, response):
                response.json({"users": ["Alice", "Bob"]})

            @app.route("/users", methods=["POST"])
            async def create_user(request, response):
                response.json({"message": "User created"}, status_code=201)
            ```
        """
        def decorator(handler: HandlerType) -> HandlerType: #type: ignore
            _handler:HandlerType = allowed_methods(methods)(handler)  
            route = Routes(path=f"{path}", 
                           handler=_handler, 
                           methods=methods, 
                           name=name,
                            **kwargs
                           )
            self.add_route(route)
            return _handler  
        return decorator  
    
    
    def url_for(self, name: str, **path_params: Any) -> URLPath:
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
            if route.name == name:
                return route.url_path_for(name, **path_params)
        raise ValueError(f"Route name '{name}' not found in router.")
    def __repr__(self) -> str:
        return f"<Router prefix='{self.prefix}' routes={len(self.routes)}>"



    

class WebsocketRoutes:
    def __init__(
        self,
        path: str,
        handler: WsHandlerType,
        middleware: Optional[WsMiddlewareType] = None
    ):
        assert callable(handler), "Route handler must be callable"
        self.raw_path = path
        self.handler:WsHandlerType = handler
        self.middleware  = middleware
        self.route_info = RouteBuilder.create_pattern(path)
        self.pattern = self.route_info.pattern
        self.param_names = self.route_info.param_names
        self.route_type = self.route_info.route_type
        self.router_middleware = None
    
    def match(self, path: str) -> Optional[Dict[str,Any]]:
        """
        Match a path against this route's pattern and return captured parameters
        """
        match = self.pattern.match(path)
        if match:
            return match.groupdict()
        return None
    
    
    def __call__(self) -> Tuple[Pattern[str],WsHandlerType,Union[WsMiddlewareType,None] ]:
        """Return the route components for registration"""
        return self.pattern, self.handler, self.middleware
    
    def __repr__(self) -> str:
        return f"<WSRoute {self.raw_path}>"
    
    async def execute_middleware_stack(self, ws :"WebsocketRoutes", **kwargs :Dict[str,Any]) -> Union[WsMiddlewareType , None]:
        """
        Executes WebSocket middleware stack after route matching.
        """
        middleware_list :List[WsMiddlewareType] = getattr(self,"router_middleware") or [] #type: ignore

        stack :List[WsMiddlewareType] = middleware_list.copy() 
        index = -1

        async def next_middleware() -> WsMiddlewareType:
            nonlocal index
            index += 1
            if index < len(stack): #type: ignore
                middleware:List[MiddlewareType] = stack[index] #type: ignore
                return await middleware(ws, next_middleware, **kwargs)#type: ignore
            else:
                # No more middleware to process
                return None #type: ignore

        return await next_middleware()
    


class WSRouter(BaseRouter):
    def __init__(self, prefix: Optional[str] = None):
        self.prefix = prefix or ""
        self.routes: List[WebsocketRoutes] = []
        self.middlewares: List[WsMiddlewareType] = []
        
        if self.prefix and not self.prefix.startswith("/"):
            warnings.warn("WSRouter prefix should start with '/'")
            self.prefix = f"/{self.prefix}"
    
    def add_ws_route(
        self, 
        route: Annotated[WebsocketRoutes, Doc("An instance of the Routes class representing a WebSocket route.")]
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
    
    def add_middleware(self, middleware: WsMiddlewareType) -> None: #type: ignore[override]
        """Add middleware to the WebSocket router"""
        if callable(middleware):
            self.middlewares.append(middleware)
    
    def get_routes(self) -> List[WebsocketRoutes]:
        """Get all WebSocket routes with their patterns, handlers, and middleware"""
        routes :List[WebsocketRoutes]= []
        for route in self.routes:
            route_ = WebsocketRoutes(
                path=route.raw_path, 
                handler=route.handler, 
                middleware=route.middleware
            )
            setattr(route_, "router_middleware", self.middlewares)
            routes.append(route_)
        return routes

    def ws_route(
        self, 
        path: Annotated[str, Doc("The WebSocket route path. Must be a valid URL pattern.")]
    ) -> Union[WsHandlerType , Any]:
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
            self.add_ws_route(WebsocketRoutes(path, handler))
            return handler

        return decorator
    
    

    

    def __repr__(self) -> str:
        return f"<WSRouter prefix='{self.prefix}' routes={len(self.routes)}>"