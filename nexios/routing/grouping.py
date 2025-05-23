import typing
import re
from nexios.types import ASGIApp, Receive, Scope, Send
from nexios.exceptions import NotFoundException
from nexios._internals.__middleware import DefineMiddleware as Middleware
from nexios._internals._route_builder import RouteBuilder
from nexios.structs import URLPath
from  .http import Router
from .base import BaseRoute
class Group(BaseRoute):
    def __init__(
        self,
        path: str,
        app: ASGIApp | None = None,
        routes: typing.List[type[BaseRoute]] | None = None,
        name: str | None = None,
        *,
        middleware: typing.List[Middleware] | None = None,
    ) -> None:
        assert path == "" or path.startswith("/"), "Routed paths must start with '/'"
        assert app is not None or routes is not None, "Either 'app=...', or 'routes=' must be specified"
        self.path = path.rstrip("/")
        if app is not None:
            self._base_app: ASGIApp = app
        else:
            self._base_app = Router(routes=routes, prefix=self.path) # type: ignore
        self.app = self._base_app
        if middleware is not None:
            for cls, args, kwargs in reversed(middleware):
                app = cls(app, *args, **kwargs)
        self.name = name
        self.raw_path = path

        self.route_info = RouteBuilder.create_pattern(path)
        self.pattern: typing.Pattern[str] = self.route_info.pattern
        self.param_names = self.route_info.param_names
        self.route_type = self.route_info.route_type

    @property
    def routes(self) -> list[BaseRoute]:
        return getattr(self._base_app, "routes", [])

    def match(self, path: str, method: str) -> typing.Tuple[typing.Any, typing.Any, typing.Any]:
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
                matched_params[key] = self.route_info.convertor[  # type: ignore
                    key
                ].convert(value)
            return match, matched_params, True
        return None, None, False

    def url_path_for(self, _name: str, **path_params: typing.Any) -> URLPath:
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


    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        print(self.app)
        await self.app(scope, receive, send)

  

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        name = self.name or ""
        return f"{class_name}(path={self.path!r}, name={name!r}, app={self.app!r})"
    
    def __call__(self, scope: Scope, receive: Receive, send: Send) -> typing.Any:
        print(self.app)
        return self.app(scope, receive, send)