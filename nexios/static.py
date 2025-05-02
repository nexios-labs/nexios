from pathlib import Path
import os
from typing import Union, List, Optional
from nexios.http.request import Request
from nexios.http.response import NexiosResponse


class StaticFilesHandler:
    def __init__(
        self,
        directory: Optional[Union[str, Path]] = None,
        directories: Optional[List[Union[str, Path]]] = None,
        url_prefix: str = "/static/",
    ):
        if directory is not None and directories is not None:
            raise ValueError("Cannot specify both 'directory' and 'directories'")
        if directory is None and directories is None:
            raise ValueError("Must specify either 'directory' or 'directories'")

        if directory is not None:
            self.directories = [self._ensure_directory(directory)]
        else:
            self.directories = [self._ensure_directory(d) for d in directories]

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

    async def __call__(self, request: Request, response: NexiosResponse):
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
            except (ValueError, RuntimeError) as e:
                continue

        return response.json("Resource not found", status_code=404)
