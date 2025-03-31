import importlib
import os
from typing import TypedDict
from nexios.application import NexiosApp
from nexios.logging import create_logger
from nexios.routing import Routes
from pathlib import Path

logger = create_logger("nexios")


class FileRouterConfig(TypedDict):
    root: str


class FileRouterPlugin:
    """
    from nexios import get_application
    from nexios.plugins import FileRouterPlugin

    app = get_application()

    FileRouterPlugin(app, config={"root": "./routes"}).setup()
    """

    app: NexiosApp
    config: FileRouterConfig

    def __init__(self, app, config: FileRouterConfig = {"root": "./routes"}):
        self.app = app
        self.config = config

        self._setup()

    def _setup(self):
        for root, _, files in os.walk(self.config["root"]):
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

    def _build_route(self, route_file_path: str) -> list[Routes]:
        handlers: list[Routes] = []
        path = self._get_path(route_file_path.replace(self.config["root"], ""))

        # Convert file path to a valid module import path
        module_path = (
            Path(route_file_path)
            .with_suffix("")  # Remove .py
            .as_posix()  # Convert Windows paths to Unix-style
            .replace("/", ".")  # Replace slashes with dots for module import
        ).lstrip(
            "."
        )  # Remove leading dot if present

        module = importlib.import_module(module_path)  # Import dynamically

        for method in ["get", "post", "patch", "put", "delete"]:
            if hasattr(module, method):
                logger.debug(f"Mapped {method.upper()} {path}")
                handlers.append(
                    Routes(
                        path.replace("\\", "/"),
                        getattr(module, method),
                        methods=[method.upper()],
                    )
                )

        return handlers
