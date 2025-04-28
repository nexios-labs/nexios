# type: ignore

import httpx
import typing
import uuid
from typing import Any, Dict, AsyncIterable, Iterable, Union, Optional, List
from .transport import NexiosAsyncTransport, WebSocketConnection, WebSocketState, WebSocketDisconnect

_RequestData = typing.Mapping[str, typing.Union[str, typing.Iterable[str], bytes]]
from nexios.application import NexiosApp


class Client(httpx.AsyncClient):
    def __init__(
        self,
        app: NexiosApp,
        root_path: str = "",
        client: tuple[str, int] = ("testclient", 5000),
        base_url: str = "http://testserver",
        raise_server_exceptions: bool = True,
        cookies: Union[httpx._types.CookieTypes, None] = None,  # type: ignore
        headers: Union[Dict[str, str], None] = None,
        follow_redirects: bool = True,
        max_retries: int = 3,
        timeout: Union[httpx._types.TimeoutTypes, float] = 5.0,  # type: ignore
        log_requests: bool = False,
        app_state: Dict[str, Any] = {},
        **kwargs: Any,
    ) -> None:
        if headers is None:
            headers = {}
        headers.setdefault("user-agent", "testclient")
        transport = NexiosAsyncTransport(
            app=app,
            app_state=app_state,
            raise_app_exceptions=raise_server_exceptions,
            root_path=root_path,
            client=client,
        )
        super().__init__(
            base_url=base_url,
            headers=headers,
            follow_redirects=follow_redirects,
            cookies=cookies,
            timeout=timeout,
            transport=transport,
            **kwargs,
        )

        self.max_retries = max_retries
        self.log_requests = log_requests

    async def handle_request(
        self,
        method: str,
        url: httpx._types.URLTypes,  # type: ignore
        *,
        content: Union[str, bytes, Iterable[bytes], AsyncIterable[bytes], None] = None,  # type: ignore
        data: Union[_RequestData, None] = None,
        files: Union[httpx._types.RequestFiles, None] = None,  # type: ignore
        json: typing.Any = None,
        params: Union[httpx._types.QueryParamTypes, None] = None,  # type: ignore
        headers: Union[httpx._types.HeaderTypes, None] = None,  # type: ignore
        cookies: Union[httpx._types.CookieTypes, None] = None,  # type: ignore
        auth: Union[httpx._types.AuthTypes, httpx._client.UseClientDefault] = httpx._client.USE_CLIENT_DEFAULT,  # type: ignore
        follow_redirects: Union[bool, httpx._client.UseClientDefault] = httpx._client.USE_CLIENT_DEFAULT,  # type: ignore
        timeout: Union[httpx._types.TimeoutTypes, httpx._client.UseClientDefault] = httpx._client.USE_CLIENT_DEFAULT,  # type: ignore
        extensions: Union[Dict[str, typing.Any], None] = None,
    ) -> httpx.Response:
        retries = 0
        last_exception = None

        response = await super().request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )
        return response

    async def get(
        self,
        url: httpx._types.URLTypes,
        *,
        params: Union[httpx._types.QueryParamTypes, None] = None,  # type: ignore
        headers: Union[httpx._types.HeaderTypes, None] = None,  # type: ignore
        cookies: Union[httpx._types.CookieTypes, None] = None,  # type: ignore
        auth: Union[httpx._types.AuthTypes, httpx._client.UseClientDefault] = httpx._client.USE_CLIENT_DEFAULT,  # type: ignore
        follow_redirects: Union[bool, httpx._client.UseClientDefault] = httpx._client.USE_CLIENT_DEFAULT,  # type: ignore
        timeout: Union[httpx._types.TimeoutTypes, httpx._client.UseClientDefault] = httpx._client.USE_CLIENT_DEFAULT,  # type: ignore
        extensions: Union[Dict[str, typing.Any], None] = None,
    ) -> httpx.Response:
        return await self.handle_request(
            "GET",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

    async def post(
        self,
        url: httpx._types.URLTypes,
        *,
        content: Union[httpx._types.RequestContent, None] = None,
        data: Union[_RequestData, None] = None,
        files: Union[httpx._types.RequestFiles, None] = None,
        json: typing.Any = None,
        params: Union[httpx._types.QueryParamTypes, None] = None,
        headers: Union[httpx._types.HeaderTypes, None] = None,
        cookies: Union[httpx._types.CookieTypes, None] = None,
        auth: Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault
        ] = httpx._client.USE_CLIENT_DEFAULT,
        follow_redirects: Union[
            bool, httpx._client.UseClientDefault
        ] = httpx._client.USE_CLIENT_DEFAULT,
        timeout: Union[
            httpx._types.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx._client.USE_CLIENT_DEFAULT,
        extensions: Union[Dict[str, typing.Any], None] = None,
    ) -> httpx.Response:
        return await self.handle_request(
            "POST",
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

    async def __aenter__(self) -> "Client":
        await super().__aenter__()
        return self

    async def __aexit__(self, *args: typing.Any) -> None:
        await super().__aexit__(*args)

    def websocket_connect(
        self,
        url: str,
        *,
        subprotocols: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> "WebSocketContextManager":
        """
        Establish a WebSocket connection to the given URL.

        Args:
            url: The URL to connect to.
            subprotocols: Optional list of subprotocols to negotiate.
            headers: Optional headers to include in the request.
            timeout: Optional timeout for the connection.

        Returns:
            A WebSocket context manager that can be used in an async with statement.
        """
        return WebSocketContextManager(
            self, url, subprotocols=subprotocols, headers=headers, timeout=timeout
        )


class WebSocketContextManager:
    """
    Async context manager for WebSocket connections.
    """
    
    def __init__(
        self,
        client: "Client",
        url: str,
        *,
        subprotocols: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ):
        self.client = client
        self.url = url
        self.subprotocols = subprotocols
        self.headers = headers
        self.timeout = timeout
        self.websocket: Optional[WebSocket] = None
    
    async def __aenter__(self) -> "WebSocket":
        """
        Connect to the WebSocket when used as a context manager with 'async with'.
        """
        if not hasattr(self, 'websocket') or self.websocket is None:
            self.websocket = await self.__call__()
        return self.websocket
        
    def __await__(self):
        """Make the WebSocketContextManager directly awaitable."""
        return self.__call__().__await__()

    async def __call__(self) -> "WebSocket":
        """Connect to the WebSocket when directly awaited."""
        import base64
        import os
        
        # Generate proper WebSocket key
        ws_key = base64.b64encode(os.urandom(16)).decode()
        
        # Set up proper WebSocket handshake headers
        if self.headers is None:
            self.headers = {}
        
        self.headers.update({
            "Upgrade": "websocket",
            "Connection": "Upgrade",
            "Sec-WebSocket-Version": "13",
            "Sec-WebSocket-Key": ws_key,
        })

        # Add subprotocols if specified
        if self.subprotocols:
            self.headers["Sec-WebSocket-Protocol"] = ", ".join(self.subprotocols)

        # Handle URL scheme
        if not self.url.startswith(('ws://', 'wss://', 'http://', 'https://')):
            # If no scheme, use ws:// with the testserver host
            base = str(self.client.base_url)
            if base.startswith('http://'):
                base = base.replace('http://', 'ws://', 1)
            elif base.startswith('https://'):
                base = base.replace('https://', 'wss://', 1)
            
            # Handle absolute and relative paths
           
            self.url = base + self.url
        elif self.url.startswith(('http://', 'https://')):
            # Convert http(s) to ws(s)
            self.url = self.url.replace('http://', 'ws://', 1).replace('https://', 'wss://', 1)

        try:
            # Make WebSocket connection request
            response = await self.client.request(
                "GET",
                self.url,
                headers=self.headers,
                timeout=self.timeout,
            )

            if response.status_code != 101:
                raise RuntimeError(
                    f"WebSocket upgrade failed with status code: {response.status_code}"
                )

            # Extract and verify WebSocket connection
            if "websocket" not in response.extensions:
                raise RuntimeError("No WebSocket connection in response")

            connection = response.extensions["websocket"]
            await connection.connect()

            # Create WebSocket instance
            websocket = WebSocket(connection)
            self.websocket = websocket

            # Verify connection is established
            if not websocket.is_connected():
                await websocket.close()
                raise RuntimeError("Failed to establish WebSocket connection")

            return websocket

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"WebSocket upgrade failed with status code: {e.response.status_code}")
        except RuntimeError:
            # Re-raise RuntimeErrors that we generated ourselves
            raise
        except Exception as e:
            # Clean up on failure
            if hasattr(self, 'websocket') and self.websocket is not None:
                await self.websocket.close()
            # raise RuntimeError(f"WebSocket connection failed: {str(e)}") from e
            print("Exceptions ", e)
    
    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self.websocket is not None:
            await self.websocket.close()


class WebSocket:
    """
    A WebSocket client for use in testing.
    """
    
    def __init__(self, connection: WebSocketConnection):
        self.connection = connection
        
    @property
    def client_state(self) -> WebSocketState:
        """The current state of the client WebSocket connection."""
        return self.connection.state
    
    @property
    def application_state(self) -> WebSocketState:
        """The current state of the application WebSocket handler."""
        return self.connection.state  # Using same state for simplicity in test client
    
    def is_connected(self) -> bool:
        """Check if the WebSocket is currently connected."""
        return self.connection.state == WebSocketState.CONNECTED
    
    async def send_text(self, data: str) -> None:
        """Send text data through the WebSocket."""
        await self.connection.send(data)
    
    async def send_bytes(self, data: bytes) -> None:
        """Send binary data through the WebSocket."""
        await self.connection.send(data)
    
    async def send_json(self, data: Any, mode: str = "text") -> None:
        """
        Send JSON data through the WebSocket.
        
        Args:
            data: The data to send (will be JSON-encoded).
            mode: The mode to send in - either "text" or "binary".
        """
        import json
        encoded = json.dumps(data)
        if mode == "text":
            await self.send_text(encoded)
        elif mode == "binary":
            await self.send_bytes(encoded.encode("utf-8"))
        else:
            raise ValueError(f"Invalid WebSocket send mode: {mode}")
    
    async def receive_text(self) -> str:
        """Receive text data from the WebSocket."""
        data = await self.connection.receive()
        if isinstance(data, bytes):
            raise RuntimeError("Expected text data, but received bytes")
        return data
    
    async def receive_bytes(self) -> bytes:
        """Receive binary data from the WebSocket."""
        data = await self.connection.receive()
        if isinstance(data, str):
            raise RuntimeError("Expected binary data, but received text")
        return data
    
    async def receive_json(self) -> Any:
        """Receive JSON data from the WebSocket."""
        import json
        data = await self.connection.receive()
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return json.loads(data)
    
    async def iter_text(self) -> AsyncIterable[str]:
        """
        Iterate over text messages from the WebSocket.
        
        Yields:
            Text messages received from the WebSocket.
        """
        try:
            while self.is_connected():
                yield await self.receive_text()
        except WebSocketDisconnect:
            pass
    
    async def iter_bytes(self) -> AsyncIterable[bytes]:
        """
        Iterate over binary messages from the WebSocket.
        
        Yields:
            Binary messages received from the WebSocket.
        """
        try:
            while self.is_connected():
                yield await self.receive_bytes()
        except WebSocketDisconnect:
            pass
    
    async def iter_json(self) -> AsyncIterable[Any]:
        """
        Iterate over JSON messages from the WebSocket.
        
        Yields:
            JSON messages received from the WebSocket.
        """
        try:
            while self.is_connected():
                yield await self.receive_json()
        except WebSocketDisconnect:
            pass
    
    async def close(self, code: int = 1000, reason: Optional[str] = None) -> None:
        """Close the WebSocket connection with the given code and reason."""
        await self.connection.close(code, reason)
    
    # These methods are still needed for direct await usage
    async def __aenter__(self) -> "WebSocket":
        return self
    
    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        await self.close()
