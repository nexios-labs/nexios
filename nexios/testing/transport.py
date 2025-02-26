import httpx
import anyio
import io
import typing
from typing import Any,Tuple
from urllib.parse import unquote

ASGIScope = dict[str, typing.Any]
Message = dict[str, typing.Any]
HeaderList = list[tuple[bytes, bytes]]

class NexiosAsyncTransport(httpx.AsyncBaseTransport):
    """Custom ASGI transport for Nexios test client, bypassing real network requests."""

    def __init__(
        self,
        app: typing.Any,
        raise_exceptions: bool = True,
        root_path: str = "",
        client: tuple[str, int] = ("testclient", 5000),
        app_state: dict[str, typing.Any] | None = None,
    ):
        self.app = app
        self.raise_exceptions = raise_exceptions
        self.root_path = root_path
        self.client = client
        self.app_state = app_state or {}

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Handles requests and routes them to the Nexios ASGI app asynchronously."""
        scheme, netloc, path, raw_path, query = self._parse_url(request)
        host, port = self._get_host_port(netloc, scheme)
        headers = self._prepare_headers(request, host, port)

        if scheme in {"ws", "wss"}:
            raise NotImplementedError("WebSocket transport is not supported yet.")

        scope = self._build_http_scope(request, scheme, path, raw_path, query, headers, host, port)
        return await self._send_request(scope, request)

    def _parse_url(self, request: httpx.Request) -> tuple[str, str, str, bytes, str]:
        """Parses the request URL into components."""
        return (
            request.url.scheme,
            request.url.netloc.decode("ascii"),
            request.url.path,
            request.url.raw_path,
            request.url.query.decode("ascii"),
        )

    def _get_host_port(self, netloc: str, scheme: str) -> tuple[str, int]:
        """Extracts the host and port from the netloc string."""
        default_ports = {"http": 80, "https": 443}
        if ":" in netloc:
            host, port = netloc.split(":", 1)
            return host, int(port)
        return netloc, default_ports.get(scheme, 80)

    def _prepare_headers(self, request: httpx.Request, host: str, port: int) -> HeaderList:
        """Prepares headers for the ASGI request."""
        headers = [(b"host", f"{host}:{port}".encode())] if "host" not in request.headers else []
        headers.extend([(key.lower().encode(), value.encode()) for key, value in request.headers.multi_items()])
        return headers

    def _build_http_scope(
        self, request: httpx.Request, scheme: str, path: str, raw_path: bytes, query: str, headers: HeaderList, host: str, port: int
    ) -> ASGIScope:
        """Constructs the ASGI scope for HTTP requests."""
        return {
            "type": "http",
            "http_version": "1.1",
            "method": request.method,
            "path": unquote(path),
            "raw_path": raw_path.split(b"?", 1)[0],
            "root_path": self.root_path,
            "scheme": scheme,
            "query_string": query.encode(),
            "headers": headers,
            "client": self.client,
            "server": [host, port],
            "state": self.app_state.copy(),
        }

    async def _send_request(self, scope: ASGIScope, request: httpx.Request) -> httpx.Response:
        """Handles ASGI request sending and response collection asynchronously."""
        request_complete = False
        response_started = False
        response_complete = anyio.Event()
        response_body = io.BytesIO()
        response_headers:list[Tuple[Any , Any]] = []
        status_code = 500

        async def receive() -> Message:
            """ASGI receive function for incoming request body."""
            nonlocal request_complete
            if request_complete:
                await response_complete.wait()
                return {"type": "http.disconnect"}

            body = await request.aread()
            request_complete = True
            return {"type": "http.request", "body": body}

        async def send(message: Message) -> None:
            """ASGI send function for sending response."""
            nonlocal response_started, status_code, response_headers
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = [(k.decode(), v.decode()) for k, v in message.get("headers")] #type:ignore
               
                
                response_started = True
            elif message["type"] == "http.response.body":
                assert response_started, "Received body before response start"
                response_body.write(message.get("body", b""))
                if not message.get("more_body", False):
                    response_body.seek(0)
                    response_complete.set()

        try:
            await self.app(scope, receive, send)
        except BaseException as exc:
            if self.raise_exceptions:
                raise exc
            status_code = 500
            response_body = io.BytesIO(b"Internal Server Error")

        if self.raise_exceptions and not response_started:
            raise RuntimeError("TestClient did not receive any response.")

        return httpx.Response(status_code, headers=dict(response_headers), content=response_body.read(), request=request)
