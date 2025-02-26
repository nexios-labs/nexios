from datetime import datetime, timedelta
from email.utils import formatdate
from typing import Any, Dict, List, Optional, Tuple, Union, Generator
from pathlib import Path
import json
from base64 import b64encode
from hashlib import sha1
import mimetypes
import typing
import os
import anyio
from typing import AsyncIterator
from anyio import AsyncFile
import http.cookies
from email.utils import format_datetime, formatdate
from datetime import datetime, timezone
from urllib.parse import quote
import hashlib
import anyio.to_thread
from nexios.structs import Headers
import stat
Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]

Receive = typing.Callable[[], typing.Awaitable[Message]]
Send = typing.Callable[[Message], typing.Awaitable[None]]

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]

class MalformedRangeHeader(Exception):
    def __init__(self, content: str = "Malformed range header.") -> None:
        self.content = content


class RangeNotSatisfiable(Exception):
    def __init__(self, max_size: int) -> None:
        self.max_size = max_size

class Response:
    """
    Base ASGI-compatible Response class with support for cookies, caching, and custom headers.
    """
    
    STATUS_CODES = {
        200: "OK",
        201: "Created",
        204: "No Content",
        301: "Moved Permanently",
        302: "Found",
        304: "Not Modified",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error",
    }

    def __init__(
        self,
        body: Union[JSONType, Any] = "",
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
    ):
        self.charset = "utf-8"
        self.status_code: int = status_code
        self._headers: List[Tuple[bytes,bytes]] = []
        self._cookies: List[Tuple[str, str, Dict[str, Any]]] = []
        self._body = self.render(body)
        self.headers = headers or {}
        
        self.content_type :str | None = content_type

    def render(self, content: typing.Any) -> bytes | memoryview:
        if content is None:
            return b""
        if isinstance(content, (bytes, memoryview)):
            return content # type: ignore
        return content.encode(self.charset) # type: ignore

    def _init_headers(self):
        raw_headers = [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in self.headers.items()]
        keys = [h[0] for h in raw_headers]
        populate_content_length = b"content-length" not in keys
        populate_content_type = b"content-type" not in keys
        body = getattr(self, "_body", None)
        if (
            body is not None
            and populate_content_length
            and not (self.status_code < 200 or self.status_code in (204, 304))
        ):
            content_length = str(len(body))
            raw_headers.append((b"content-length", content_length.encode("latin-1")))
        content_type :str | None = self.content_type
        if content_type is not None and populate_content_type:
            if content_type.startswith("text/") and "charset=" not in content_type.lower():
                content_type += "; charset=" + self.charset
            self._headers.append((b"content-type", content_type.encode("latin-1")))
        self._headers.extend(raw_headers)
        
    def set_cookie(
        self,
        key: str,
        value: str  = "",
        max_age: int | None = None,
        expires: datetime | str | int | None = None,
        path: str | None = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: typing.Literal["lax", "strict", "none"] | None = "lax",
    ) -> None:
        cookie: http.cookies.BaseCookie[str] = http.cookies.SimpleCookie()
        cookie[key] = value
        if max_age is not None:
            cookie[key]["max-age"] = max_age
        if expires is not None:
            if isinstance(expires, datetime):
                expires = datetime.now(timezone.utc) 
                cookie[key]["expires"] = format_datetime(expires, usegmt=True)
            else:
                cookie[key]["expires"] = expires
        if path is not None:
            cookie[key]["path"] = path
        if domain is not None:
            cookie[key]["domain"] = domain
        if secure:
            cookie[key]["secure"] = True
        if httponly:
            cookie[key]["httponly"] = True
        if samesite is not None:
            assert samesite.lower() in [
                "strict",
                "lax",
                "none",
            ], "samesite must be either 'strict', 'lax' or 'none'"
            cookie[key]["samesite"] = samesite
        cookie_val = cookie.output(header="").strip()
        self.header("set-cookie" ,  cookie_val)

    def delete_cookie(self, key: str, path: str = "/", domain: Optional[str] = None) -> None:
        """Delete a cookie by setting its expiry to the past."""
        self.set_cookie(
            key=key,
            value="",
            max_age=0,
            expires=0,
            path=path,
            domain=domain
        )

    def enable_caching(self, max_age: int = 3600, private: bool = True) -> None:
        """Enable caching with the specified max age (in seconds)."""
        cache_control: List[str] = []
        if private:
            cache_control.append("private")
        else:
            cache_control.append("public")
            
        cache_control.append(f"max-age={max_age}")
        self.headers["cache-control"] = ", ".join(cache_control)
        
        etag = self._generate_etag()
        self.headers["etag"] = etag
        
        expires = datetime.utcnow() + timedelta(seconds=max_age)  # type: ignore
        self.headers["expires"] = formatdate(expires.timestamp(), usegmt=True)

    def disable_caching(self) -> None:
        """Disable caching for this response."""
        self.headers["cache-control"] = "no-store, no-cache, must-revalidate, max-age=0"
        self.headers["pragma"] = "no-cache"
        self.headers["expires"] = "0"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Make the response callable as an ASGI application."""
        self._init_headers()
        
        await send({
            'type': 'http.response.start',
            'status': self.status_code,
            'headers': self._headers,
        })
        
        await send({
            'type': 'http.response.body',
            'body': self._body,
        })


    def _generate_etag(self) -> str:
        """Generate an ETag for the response content."""
        content_hash = sha1()
        content_hash.update(self._body) #type:ignore
        return f'W/"{b64encode(content_hash.digest()).decode("utf-8")}"'
    
    def header(self, key :str, value:str):
        header :Tuple[bytes, bytes]= (key.encode("utf-8"), value.encode("utf-8"))
        self._headers.append(header)
        return self
    
 
        
    
    


class PlainTextResponse(Response):
    def __init__(self, body:JSONType =  "", status_code: int = 200, headers: Dict[str, str] | None = None, content_type: str = "text/plain"):
        super().__init__(body, status_code, headers, content_type)
class JSONResponse(Response):
    """
    Response subclass for JSON content.
    """
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        indent: Optional[int] = None,
        ensure_ascii: bool = True,
    ):
        try:
            body = json.dumps(
                content,
                indent=indent,
                ensure_ascii=ensure_ascii,
                allow_nan=False,
                default=str
            )
        except (TypeError, ValueError) as e:
            raise ValueError(f"Content is not JSON serializable: {str(e)}")
            
        super().__init__(
            body=body,
            status_code=status_code,
            headers=headers,
            content_type="application/json"
        )


class HTMLResponse(Response):
    """
    Response subclass for HTML content.
    """
    def __init__(
        self,
        content: Union[str, JSONType],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            body=content,
            status_code=status_code,
            headers=headers,
            content_type="text/html; charset=utf-8"
        )


class FileResponse(Response):
    """
    Enhanced FileResponse class with AnyIO for asynchronous file streaming,
    support for range requests, and multipart responses.
    """
    chunk_size = 64 * 1024  # 64KB chunks

    def __init__(
        self,
        path: Union[str, Path],
        filename: Optional[str] = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_disposition_type: str = "inline",
    ):
        super().__init__(headers=headers)
        self.path = Path(path)
        self.filename = filename or self.path.name
        self.content_disposition_type = content_disposition_type
        self.status_code = status_code

        self.headers = headers or {}
        content_type, _ = mimetypes.guess_type(str(self.path))
        self.header('content-type', content_type or 'application/octet-stream')
        self.header('content-disposition' ,f'{content_disposition_type}; filename="{self.filename}"')
        self.header('accept-ranges','bytes')         

        self._ranges: List[Tuple[int, int]] = []
        self._multipart_boundary: Optional[str] = None
    def set_stat_headers(self, stat_result: os.stat_result) -> None:
        content_length = str(stat_result.st_size)
        last_modified = formatdate(stat_result.st_mtime, usegmt=True)
        etag_base = str(stat_result.st_mtime) + "-" + str(stat_result.st_size)
        etag = f'"{hashlib.md5(etag_base.encode(), usedforsecurity=False).hexdigest()}"'

        self.headers.setdefault("content-length", content_length)
        self.headers.setdefault("last-modified", last_modified)
        self.headers.setdefault("etag", etag)
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Handle the ASGI response, including range requests."""
        
        try:
            stat_result = await anyio.to_thread.run_sync(os.stat, self.path)
            self.set_stat_headers(stat_result)
        except FileNotFoundError:
            raise RuntimeError(f"File at path {self.path} does not exist.")
        else:
            mode = stat_result.st_mode
            if not stat.S_ISREG(mode):
                raise RuntimeError(f"File at path {self.path} is not a file.")
        
        
        range_header = Headers(scope=scope).get("Range")
        if range_header:
            self._handle_range_header(range_header)

        await self._send_response(scope, receive, send)
  

    def _handle_range_header(self, range_header: str) -> None:
        """Parse and validate the Range header."""
        file_size = self.path.stat().st_size
        
        try:
            unit, ranges = range_header.strip().split('=')
            if unit != 'bytes':
                raise ValueError("Only byte ranges are supported")

            self._ranges = []
            for range_str in ranges.split(','):
                range = range_str.split('-')
                start :int = int(range[0])
                end :int =int(range[-1])
                start = int(start) if start else 0
                end :int = int(end) if end else file_size - 1

                if start < 0 or end >= file_size or start > end:
                    raise ValueError("Invalid range")

                self._ranges.append((start, end))

            if len(self._ranges) == 1:
                start, end = self._ranges[0]
                content_length = end - start + 1
                self.header('content-range', f'bytes {start}-{end}/{file_size}')
                self.header('content-length', str(content_length))
                self.status_code = 206
            elif len(self._ranges) > 1:
                
                self._multipart_boundary = self._generate_multipart_boundary()
                self.header('content-type',f'multipart/byteranges; boundary={self._multipart_boundary}')
                self.status_code = 206  

        except ValueError as _: 
         
            self.header('content-range',f'bytes */{file_size}')
            self.status_code = 416  

    async def _send_response(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Send the file response, handling range requests and multipart responses."""
       
        await send({
            'type': 'http.response.start',
            'status': self.status_code,
            'headers': self._headers,
        })

        if self.status_code == 416: 
            await send({
                'type': 'http.response.body',
                'body': b'',
            })
            return

        async with await anyio.open_file(self.path, 'rb') as file:
            
            if self._multipart_boundary:
                for start, end in self._ranges:
                    await self._send_multipart_chunk(file, start, end, send)
                await send({
                    'type': 'http.response.body',
                    'body': f'--{self._multipart_boundary}--\r\n'.encode('utf-8'),
                    'more_body': False,
                })
            elif self._ranges:
                start, end = self._ranges[0]
                await self._send_range(file, start, end, send) #type:ignore
            else:
                await self._send_full_file(file, send) #type:ignore

    async def _send_full_file(self, file: AsyncIterator[bytes], send: Send) -> None:
        """Send the entire file in chunks using AnyIO."""
        while True:
            chunk = await file.read(self.chunk_size) #type:ignore
            if not chunk:
                break
            await send({
                'type': 'http.response.body',
                'body': chunk,
                'more_body': True,
            })
        await send({
            'type': 'http.response.body',
            'body': b'',
            'more_body': False,
        })

    async def _send_range(self, file: AsyncFile[bytes], start: int, end: int, send: Send) -> None:
        """Send a single range of the file using AnyIO."""
        await file.seek(start)
        remaining = end - start + 1
        self.header('content-length',str(remaining))
        
        while remaining > 0:
            chunk_size = min(self.chunk_size, remaining)
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            await send({
                'type': 'http.response.body',
                'body': chunk,
                'more_body': True,
            })
            remaining -= len(chunk)
        await send({
            'type': 'http.response.body',
            'body': b'',
            'more_body': False,
            
        })

    async def _send_multipart_chunk(self, file: AsyncFile[bytes], start: int, end: int, send: Send) -> None:
        """Send a multipart chunk for a range using AnyIO."""
        await file.seek(start)
        remaining = end - start + 1

        boundary = f'--{self._multipart_boundary}\r\n'
        header = next((value for key, value in self._headers if key == b"content-type"), None)
        headers = f'Content-Type: {header}\r\nContent-Range: bytes {start}-{end}/{self.path.stat().st_size}\r\n\r\n' #type:ignore[str-bytes-safe]
        await send({
            'type': 'http.response.body',
            'body': (boundary + headers).encode('utf-8'),
            'more_body': True,
        })

        while remaining > 0:
            chunk_size = min(self.chunk_size, remaining)
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            await send({
                'type': 'http.response.body',
                'body': chunk,
                'more_body': True,
            })
            remaining -= len(chunk)

    def _generate_multipart_boundary(self) -> str:
        """Generate a unique multipart boundary string."""
        return f"boundary_{os.urandom(16).hex()}"


class StreamingResponse(Response):
    """
    Response subclass for streaming content.
    """
    def __init__(
        self,
        content: AsyncIterator[Union[str, bytes]],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "text/plain",
    ):
        super().__init__(headers=headers)
        
        self.content_iterator = content
        self.status_code = status_code
        self._cookies: List[Tuple[str, str, Dict[str, Any]]] = []
        
        self.content_type = content_type
        self.headers['content-type'] = self.content_type
        
        self.headers.pop('content-length', None)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Stream the content."""
        await send({
            'type': 'http.response.start',
            'status': self.status_code,
            'headers': self._headers,
        })

        async for chunk in self.content_iterator:
            if isinstance(chunk, str):
                chunk = chunk.encode('utf-8')
            await send({
                'type': 'http.response.body',
                'body': chunk,
                'more_body': True
            })
            
        await send({
            'type': 'http.response.body',
            'body': b'',
            'more_body': False
        })


class RedirectResponse(Response):
    """
    Response subclass for HTTP redirects.
    """
    def __init__(
        self,
        url: str,
        status_code: int = 302,
        headers: Dict[str, str] = {},
    ):
        if not 300 <= status_code < 400:
            raise ValueError("Status code must be a valid redirect status")
            
        headers["location"] = quote(str(url), safe=":/%#?=@[]!$&'()*+,;")
        
        super().__init__(
            body="",
            status_code=status_code,
            headers=headers
        )


class NexiosResponse:
    """
    A wrapper class that provides a fluent interface for different response types.
    """
    def __init__(self):
        self._body: Optional[JSONType] = None
        self._content_type = "application/json"
        self._response: Response = Response()
        self._cookies: List[Dict[str, Any]] = []
        self._status_code = self._response.status_code
        self._delete_cookies: List[Dict[str, Any]] = []
        self.headers = {}

    
    def text(self, content: JSONType, status_code:int = 200, headers: Dict[str, Any] = {}):
        """Send plain text or HTML content."""
        header_store = self._response._headers.copy() # type: ignore[reportPrivateUsage]
        
        self._response = PlainTextResponse(body=content, status_code=status_code,headers=headers)
        self._response._headers.extend(header_store)   # type: ignore[reportPrivateUsage]
        
        return self

    def json(self, data: Union[str, List[Any], 
                               Dict[str, Any]], 
             status_code: int= 200, headers: Dict[str, Any] = {}, 
             indent: Optional[int] = None,
                ensure_ascii: bool = True,):
        """Send JSON response."""
        header_store = self._response._headers.copy() # type: ignore[reportPrivateUsage]
        self._response = JSONResponse(
            content=data,
            status_code=status_code,
            headers=headers,
            indent=indent,
            ensure_ascii=ensure_ascii
        )
        self._response._headers.extend(header_store)   # type: ignore[reportPrivateUsage]

        return self
    def empty(self, status_code:int = 200, headers: Dict[str, Any] = {}):
        """Send an empty response."""
        header_store = self._response._headers.copy() # type: ignore[reportPrivateUsage]
        
        self._response = Response(
            status_code=status_code,
            headers=headers
        )
        self._response._headers.extend(header_store) # type: ignore[reportPrivateUsage]
        
        return self._response
        
    def html(self, content: str, status_code: int = 200, headers: Dict[str, Any] = {}):
        """Send HTML response."""
        
        header_store = self._response._headers.copy() # type: ignore[reportPrivateUsage]
        self._response = HTMLResponse(
            content=content,
            status_code=status_code,
            headers=headers
        )
        self._response._headers.extend(header_store) # type: ignore[reportPrivateUsage]
        
        return self

    def file(self, path: str, filename: Optional[str] = None, content_disposition_type: str = "inline"):
        """Send file response."""
        header_store = self._response._headers.copy() # type: ignore[reportPrivateUsage]
        
        self._response = FileResponse(
            path=path,
            filename=filename,
            status_code=self._status_code,  # type: ignore
            headers=self._response.headers,
            content_disposition_type=content_disposition_type,
        )
        self._response._headers.extend(header_store) # type: ignore[reportPrivateUsage]
        
        return self

    def stream(self, iterator: Generator[Union[str, bytes],Any, Any], content_type: str = "text/plain"):
        """Send streaming response."""
        header_store = self._response._headers.copy() # type: ignore[reportPrivateUsage]
        
        self._response = StreamingResponse(
            content=iterator,  # type: ignore
            status_code=self._status_code,
            headers=self._response.headers,
            content_type=content_type
        )
        self._response._headers.extend(header_store) # type: ignore[reportPrivateUsage]
        
        return self

    def redirect(self, url: str, status_code: int = 302):
        """Send redirect response."""
        header_store = self._response._headers.copy() # type: ignore[reportPrivateUsage]
        
        self._response = RedirectResponse(
            url=url,
            status_code=status_code,
            headers=self._response.headers
        )
        self._response._headers.extend(header_store) # type: ignore[reportPrivateUsage]
        
        return self

    def status(self, status_code: int):
        """Set response status code."""
        self._response.status_code = status_code
        return self

    def header(self, key: str, value: str):
        """Set a response header."""
        self._response.header(key, value)
        return self

    def set_cookie(
        self,
        key: str,
        value: str,
        max_age: Optional[int] = None,
        expires: Optional[Union[str, datetime, int]] = None,
        path: str = "/",
        domain: Optional[str] = None,
        secure: bool = True,
        httponly: bool = False,
        samesite: typing.Literal["lax", "strict", "none"] | None = "lax",
    ):
        """Set a response cookie."""
        self._response.set_cookie(
            key  = key,
            value= value,
            max_age = max_age,
            expires =  expires,
            path= path,
            domain= domain,
            secure=secure,
            httponly= httponly,
            samesite= samesite
        )
        return self
    
    def delete_cookie(
        self,
        key: str,
        path: str = "/",
        domain: Optional[str] = None,
    ):
        """Delete a response cookie."""
        self._response.delete_cookie(
            key  = key,
            path= path,
            domain= domain,

            
        )
        return self

    def cache(self, max_age: int = 3600, private: bool = True):
        """Enable response caching."""
        
        self._response.enable_caching(max_age, private)
        return self

    def no_cache(self):
        """Disable response caching."""
       
        self._response.disable_caching()
        return self

    def resp(
        self,
        body: Union[JSONType, Any] = "",
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "text/plain",
    ):
        """
        Provides access to the purest form of the response object.
        """
        _resp = Response(
            body=body,
            status_code=status_code,
            headers=headers,
            content_type=content_type
        )
        self._response = _resp
        return self

   

    def get_response(self) -> Response:
        """Make the response ASGI-compatible."""
        
        response = self._response
        return response

       
        
    def __str__(self):
        return f"Response [{self._status_code} {self._body}]" 
    
    
    
