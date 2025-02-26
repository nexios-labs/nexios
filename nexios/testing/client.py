#type:ignore

import httpx
import typing
from typing import Any,Dict,AsyncIterable,Iterable
from .transport import NexiosAsyncTransport
_RequestData = typing.Mapping[str, typing.Union[str, typing.Iterable[str], bytes]]
from nexios.application import NexiosApp

class Client(httpx.AsyncClient):
    def __init__(
        self,
        app :NexiosApp,
        root_path :str = "",
        client: tuple[str, int] = ("testclient", 5000),
        base_url: str = "http://testserver",
        raise_server_exceptions: bool = True,
        cookies: httpx._types.CookieTypes | None = None, #type:ignore
        headers: dict[str, str] | None = None,
        follow_redirects: bool = True,
        max_retries: int = 3,
        timeout: httpx._types.TimeoutTypes = 5.0, #type:ignore
        log_requests: bool = False,
        app_state :Dict[str,Any] = {},
        **kwargs: Any,
    ) -> None:
        if headers is None:
            headers = {}
        headers.setdefault("user-agent", "testclient")
        transport = NexiosAsyncTransport(
            app=app,
            app_state=app_state,
            raise_exceptions=raise_server_exceptions,
            root_path=root_path,
            client=client
            
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
    async def request_with_retries(
       
        self,
        method: str,
        url: httpx._types.URLTypes, #type:ignore
        *,
        content: str | bytes | Iterable[bytes] | AsyncIterable[bytes] = None, #type:ignore
        data: _RequestData | None = None,
        files: httpx._types.RequestFiles | None = None, #type:ignore
        json: typing.Any = None,
        params: httpx._types.QueryParamTypes | None = None,#type:ignore
        headers: httpx._types.HeaderTypes | None = None,#type:ignore
        cookies: httpx._types.CookieTypes | None = None,#type:ignore
        auth: httpx._types.AuthTypes | httpx._client.UseClientDefault = httpx._client.USE_CLIENT_DEFAULT,#type:ignore
        follow_redirects: bool | httpx._client.UseClientDefault = httpx._client.USE_CLIENT_DEFAULT,#type:ignore
        timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx._client.USE_CLIENT_DEFAULT,#type:ignore
        extensions: dict[str, typing.Any] | None = None,
    ) -> httpx.Response: 
        retries = 0
        last_exception = None

        while retries < self.max_retries:
            try:
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
                if self.log_requests:
                    print(f"Request: {method} {url} - Status: {response.status_code}")
                return response
            except Exception as e:
                last_exception = e
                retries += 1
                if self.log_requests:
                    print(f"Retry {retries}/{self.max_retries} for {method} {url} due to {e}")

        raise last_exception or Exception("Max retries exceeded")

    async def get(
        self,
        url: httpx._types.URLTypes,
        *,
        params: httpx._types.QueryParamTypes | None = None, 
        headers: httpx._types.HeaderTypes | None = None,
        cookies: httpx._types.CookieTypes | None = None,
        auth: httpx._types.AuthTypes | httpx._client.UseClientDefault = httpx._client.USE_CLIENT_DEFAULT,
        follow_redirects: bool | httpx._client.UseClientDefault = httpx._client.USE_CLIENT_DEFAULT,
        timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx._client.USE_CLIENT_DEFAULT,
        extensions: dict[str, typing.Any] | None = None,
    ) -> httpx.Response:
        return await self.request_with_retries(
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
        content: httpx._types.RequestContent | None = None,
        data: _RequestData | None = None,
        files: httpx._types.RequestFiles | None = None,
        json: typing.Any = None,
        params: httpx._types.QueryParamTypes | None = None,
        headers: httpx._types.HeaderTypes | None = None,
        cookies: httpx._types.CookieTypes | None = None,
        auth: httpx._types.AuthTypes | httpx._client.UseClientDefault = httpx._client.USE_CLIENT_DEFAULT,
        follow_redirects: bool | httpx._client.UseClientDefault = httpx._client.USE_CLIENT_DEFAULT,
        timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx._client.USE_CLIENT_DEFAULT,
        extensions: dict[str, typing.Any] | None = None,
    ) -> httpx.Response:
        return await self.request_with_retries(
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