from pathlib import Path
from pathlib import Path
import os
from typing import Union
from nexios.http.request import Request
from nexios.http.response import NexiosResponse
class StaticFilesHandler:
    
    def __init__(self, directory: Union[str, Path], url_prefix: str = "/static/"):
        
        self.directory = Path(directory).resolve()
        self.url_prefix = url_prefix.strip("/") + "/"
        
        if not self.directory.exists():
            os.makedirs(self.directory)
        
        if not self.directory.is_dir():
            raise ValueError(f"{directory} is not a directory")

    def _is_safe_path(self, path: Path) -> bool:
        """Check if the path is safe to serve"""
        try:
            full_path = path.resolve()
            return str(full_path).startswith(str(self.directory))
        except (ValueError, RuntimeError):
            return False

    async def __call__(self, request :Request, response :NexiosResponse):
        path = request.url.path
        if path.startswith("/"):
            path = path[1:]
        
        if path.startswith(self.url_prefix.strip("/")):
            path = path[len(self.url_prefix.strip("/")):]
        
        file_path = f"{self.directory}{path}"
        if not self._is_safe_path(Path(file_path)):
            return response.status(403)
            
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return response.json("Resource not found !",status_code = 404)
            

        response.file(file_path,content_disposition_type="inline")
  