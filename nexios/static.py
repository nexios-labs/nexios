import os
import warnings
from pathlib import Path
from typing import List, Optional, Union

from nexios.http import Request, Response
from nexios.routing import BaseRouter
from nexios.types import Receive, Scope, Send


class StaticFilesHandler:
    def __init__(
        self,
        directory: Optional[Union[str, Path]] = None,
        directories: Optional[List[Union[str, Path]]] = None,
        url_prefix: str = "/static/",
    ):
        warnings.warn(
            "StaticFilesHandler is deprecated and will be removed in a future version. "
            "Please use StaticFiles instead with app.register(). Example:\n"
            "static_files = StaticFiles(directory='path/to/static')\n"
            "app.register(static_files, prefix='/static')",
            DeprecationWarning,
            stacklevel=2,
        )
        if directory is not None and directories is not None:
            raise ValueError("Cannot specify both 'directory' and 'directories'")
        if directory is None and directories is None:
            raise ValueError("Must specify either 'directory' or 'directories'")

        if directory is not None:
            self.directories = [self._ensure_directory(directory)]
        else:
            self.directories = [self._ensure_directory(d) for d in directories or []]

        self.url_prefix = url_prefix.rstrip("/") + "/"

    def _ensure_directory(self, path: Union[str, Path]) -> Path:
        """Ensure directory exists and return resolved Path"""
        directory = Path(path).resolve()
        if not directory.exists():
            os.makedirs(directory, exist_ok=True)
        if not directory.is_dir():
            raise ValueError(f"{directory} is not a directory")
        return directory

    def _is_safe_path(self, path: Path) -> bool:
        """Check if the path is safe to serve"""
        try:
            full_path = path.resolve()
            return any(
                str(full_path).startswith(str(directory))
                for directory in self.directories
            )
        except (ValueError, RuntimeError):
            return False

    async def __call__(self, request: Request, response: Response):
        path = request.path_params.get("path", "")

        if not path:
            return response.json("Invalid static file path", status_code=400)

        for directory in self.directories:
            try:
                file_path = (directory / path).resolve()

                if self._is_safe_path(file_path) and file_path.is_file():
                    return response.file(
                        str(file_path), content_disposition_type="inline"
                    )
            except (ValueError, RuntimeError):
                continue

        return response.json("Resource not found", status_code=404)


class StaticFiles(BaseRouter):
    def __init__(
        self,
        directory: Optional[Union[str, Path]] = None,
        directories: Optional[List[Union[str, Path]]] = None,
    ):
        if not directories:
            directories = [directory] if directory else []
        self.directories = [self._ensure_directory(d) for d in directories or []]

    def _ensure_directory(self, path: Union[str, Path]) -> Path:
        """Ensure directory exists and return resolved Path"""
        directory = Path(path).resolve()
        if not directory.exists():
            os.makedirs(directory, exist_ok=True)
        if not directory.is_dir():
            raise ValueError(f"{directory} is not a directory")
        return directory

    def _is_safe_path(self, path: Path) -> bool:
        """Check if the path is safe to serve"""
        try:
            full_path = path.resolve()
            return any(
                str(full_path).startswith(str(directory))
                for directory in self.directories
            )
        except (ValueError, RuntimeError):
            return False

    async def _handle(self, request: Request, response: Response):
        path = request.scope.get("path", "").lstrip("/")
        for directory in self.directories:
            try:
                file_path = (directory / path).resolve()
                if self._is_safe_path(file_path) and file_path.is_file():
                    return response.file(
                        str(file_path), content_disposition_type="inline"
                    )
            except (ValueError, RuntimeError):
                continue

        return response.json("Resource not found", status_code=404)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        request = Request(scope, receive)
        response = Response(request)
        await self._handle(request, response)
        result = response.get_response()
        if result is not None:
            response = result
        await response(scope, receive, send)
