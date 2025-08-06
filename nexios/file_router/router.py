import importlib
import os
from pathlib import Path
from typing import List, Optional, TypedDict

from nexios.application import NexiosApp
from nexios.logging import create_logger
from nexios.routing import Routes

logger = create_logger("nexios")


class FileRouterConfig(TypedDict):
    root: str
    exempt_paths: Optional[List[str]]
    exclude_from_schema: Optional[bool]


class FileRouter:
    """
    from nexios import NexiosApp
    from nexios.plugins import FileRouterPlugin

    app = NexiosApp()

    FileRouter(app, config={"root": "./routes"})
    """

    app: NexiosApp
    config: FileRouterConfig

    def __init__(
        self,
        app,
        config: FileRouterConfig = {
            "root": "./routes",
            "exempt_paths": [],
            "exclude_from_schema": False,
        },
    ):
        self.app = app
        self.config = config

        self._setup()

    def _setup(self):
        exempt_paths = set(
            os.path.abspath(path)
            for path in self.config.get("exempt_paths", [])  # type:ignore
        )  # type:ignore
        for root, _, files in os.walk(self.config["root"]):
            if os.path.abspath(root) in exempt_paths:
                continue  # Skip the exempted paths
            for file in files:
                file_path = os.path.join(root, file)
                if not file_path.endswith("route.py"):
                    continue

                for route in self._build_route(file_path):
                    self.app.add_route(route)

    def _get_path(self, route_file_path: str) -> str:
        path = route_file_path.replace("route.py", "")
        segments = [
            "{%s}" % segment.replace("_", "") if segment.startswith("_") else segment
            for segment in path.split("/")
        ]

        return "/".join(segments)

    def restrict_slash(self, s: str) -> bool:
        return s.strip() != "/"

    def _build_route(self, route_file_path: str) -> list[Routes]:
        handlers: list[Routes] = []
        path = self._get_path(route_file_path.replace(self.config["root"], ""))

        # Convert file path to a valid module import path
        module_path = (
            Path(route_file_path).with_suffix("").as_posix().replace("/", ".")
        ).lstrip(".")  # Remove leading dot if present

        module = importlib.import_module(module_path)  # Import dynamically

        for attr_name in dir(module):
            methods = ["get", "post", "patch", "put", "delete"]
            is_route = attr_name in methods or hasattr(
                getattr(module, attr_name), "_is_route"
            )

            if is_route:
                handler_function = getattr(module, attr_name)
                logger.debug(f"Mapped {attr_name} {path}")
                path = getattr(handler_function, "_path", path.replace("\\", "/"))
                if attr_name in ["get", "post", "patch", "put", "delete"]:
                    methods = [attr_name.upper()]
                else:
                    methods = getattr(handler_function, "_allowed_methods", ["GET"])
                handlers.append(
                    Routes(
                        path=path.rstrip("/") if self.restrict_slash(path) else path,
                        handler=handler_function,  # type:ignore
                        methods=methods,
                        name=getattr(handler_function, "_name", ""),
                        summary=getattr(handler_function, "_summary", ""),
                        description=getattr(handler_function, "_description", ""),
                        responses=getattr(handler_function, "_responses", {}),
                        request_model=getattr(handler_function, "_request_model", None),
                        middleware=getattr(handler_function, "_middleware", []),
                        tags=getattr(handler_function, "_tags", []),
                        security=getattr(handler_function, "_security", []),
                        operation_id=getattr(handler_function, "_operation_id", ""),
                        deprecated=getattr(handler_function, "_deprecated", False),
                        parameters=getattr(handler_function, "_parameters", []),
                        exclude_from_schema=getattr(
                            handler_function,
                            "_exclude_from_schema",
                            self.config.get("exclude_from_schema", False),
                        ),  # type: ignore
                    )
                )

        return handlers
