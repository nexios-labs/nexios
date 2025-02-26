from __future__ import annotations
from enum import Enum
from typing import TypeAlias,Callable,Type,Awaitable,Any
import typing
from .http.request import Request
from .http.response import NexiosResponse,Response
from .websockets import WebSocket
class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    
AppType = typing.TypeVar("AppType")

Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]

Receive = typing.Callable[[], typing.Awaitable[Message]]
Send = typing.Callable[[Message], typing.Awaitable[None]]
    
MiddlewareType: TypeAlias = Callable[
    [Request, NexiosResponse, Callable[..., Awaitable[None]]], 
    Awaitable[typing.Union[NexiosResponse , None]]
]
WsMiddlewareType :TypeAlias = Callable[[Type[WebSocket],Type[Callable[...,Awaitable[Message]]]], Type[Send]]  

WsHandlerType = Callable[..., Awaitable[typing.Union[Send , Message]]]
HandlerType = Callable[..., Awaitable[Any]]
ExceptionHandlerType = Callable[[Request,Response,Exception],typing.Coroutine[Any,Any,Any]]

ASGIApp = typing.Callable[[Scope, Receive, Send], typing.Awaitable[None]]

