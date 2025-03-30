# Experimental

import gzip
from io import BytesIO
from typing import Callable, Any
from nexios.middlewares.base import BaseMiddleware
from nexios.http import Request, Response
from nexios.config import get_config


class GzipMiddleware(BaseMiddleware):
    def __init__(self):
        config = get_config().gzip if hasattr(get_config(), "gzip") else None
        self.minimum_size = getattr(config, "minimum_size", 500)
        self.content_types = getattr(
            config,
            "content_types",
            [
                "text/plain",
                "text/html",
                "text/css",
                "application/javascript",
                "application/json",
                "application/xml",
            ],
        )
        self.compression_level = getattr(config, "compression_level", 6)

    async def process_request(
        self, request: Request, response: Response, call_next: Callable[..., Any]
    ):
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding.lower():
            await call_next()
            return
        await call_next()
        if self.should_compress(response):
            self.compress_response(response)

    def should_compress(self, response: Response) -> bool:
        content_length = int(
            response.headers.get("Content-Length", "0") or 0
        )  # dirty code, fix later
        content_type = response.content_type  # type:ignore

        return (
            content_length >= self.minimum_size and content_type in self.content_types
        )

    def compress_response(self, response: Response):
        buffer = BytesIO()
        with gzip.GzipFile(
            mode="wb", fileobj=buffer, compresslevel=self.compression_level
        ) as gzip_file:
            gzip_file.write(response.body)

        response.resp(buffer.getvalue())
        response.header("Content-Encoding", "gzip")
        response.header("Content-Length", str(len(response.body)), overide=True)
        response.header("Vary", "Accept-Encoding")

    async def process_response(self, request: Request, response: Response):
        pass
