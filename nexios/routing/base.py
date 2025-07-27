from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from nexios.types import ASGIApp, Receive, Scope, Send


class BaseRouter(ABC):
    """
    Base class for routers. This class should not be instantiated directly.
    Subclasses should implement the `__call__` method to handle specific routing logic.
    """

    def __init__(self, prefix: Optional[str] = None):
        self.prefix = prefix or ""
        self.routes: List[Type[BaseRoute]] = []
        self.middleware: List[Any] = []
        self.sub_routers: Dict[str, ASGIApp] = {}

        if self.prefix and not self.prefix.startswith("/"):
            warnings.warn("Router prefix should start with '/'")
            self.prefix = f"/{self.prefix}"

    @abstractmethod
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        raise NotImplementedError("Subclasses must implement this method")

    def add_middleware(self, middleware: Any) -> None:
        self.middleware.append(middleware)

    def build_middleware_stack(self, app: ASGIApp) -> ASGIApp:
        for mdw in reversed(self.middleware):
            app = mdw(app)
        return app

    def mount_router(self, path: str, app: ASGIApp) -> None:
        path = path.rstrip("/")
        if not path.startswith("/"):
            path = f"/{path}"
        self.sub_routers[path] = app

    def __repr__(self) -> str:
        return f"<BaseRouter prefix='{self.prefix}' routes={len(self.routes)}>"


class BaseRoute(ABC):
    """
    Base class for routes. This class should not be instantiated directly.
    Subclasses should implement the `matches` method to handle specific routing logic.
    """

    def __init__(
        self, path: str, methods: Optional[List[str]] = None, **kwargs: Dict[str, Any]
    ) -> None:
        self.path = path
        self.methods = methods or []

    @abstractmethod
    def match(self, scope: Scope) -> bool:
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def url_path_for(self, name: str, **path_params: Any) -> str:
        raise NotImplementedError("Subclasses must implement this method")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.match(scope):
            await self.handle(scope, receive, send)
        else:
            raise ValueError("Route does not match the scope")
