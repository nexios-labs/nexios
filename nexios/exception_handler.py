from __future__ import annotations
import typing
from nexios.exceptions import HTTPException
from nexios.http import Request,Response
from nexios.types import ExceptionHandlerType
from nexios.config import get_config
import traceback
from nexios.auth.exceptions import AuthenticationFailed,AuthErrorHandler
from nexios.exceptions import NotFoundException
from nexios.handlers.not_found import handle_404_error
def _lookup_exception_handler(exc_handlers :typing.Dict[typing.Any[int ,Exception],ExceptionHandlerType], exc: Exception) :
    
    for cls in type(exc).__mro__:
        if cls in exc_handlers: #type: ignore
            return exc_handlers[cls]
    return None
async def wrap_app_handling_exceptions(request :Request, response :Response, call_next :typing.Callable[...,typing.Awaitable[None]], exception_handlers :typing.Dict[type[Exception],ExceptionHandlerType], status_handlers:typing.Dict[int ,ExceptionHandlerType] ) -> typing.Any:
   
    try:
        exception_handlers, status_handlers =  exception_handlers, status_handlers
    except KeyError:
        exception_handlers, status_handlers = {}, {}

    

    try:
        await call_next() 
    except Exception as exc:
        handler :typing.Any[ExceptionHandlerType,None]= None #type: ignore

        if isinstance(exc, HTTPException):
            handler :ExceptionHandlerType = status_handlers.get(exc.status_code) #type: ignore

        if handler is None: #type: ignore
            handler = _lookup_exception_handler(exception_handlers, exc)
            if not handler:
                raise exc
            error = traceback.format_exc()
            return  await handler(request,response,exc)
        raise exc
       


class ExceptionMiddleware:
    def __init__(self ) -> None:
        self.debug = get_config().debug or False # TODO: We ought to handle 404 cases if debug is set.
        self._status_handlers:typing.Dict[int,ExceptionHandlerType]= {}
        self._exception_handlers :dict[type[Exception],ExceptionHandlerType] = {HTTPException: self.http_exception, #type:ignore[dict-item]
                                                                                 AuthenticationFailed:AuthErrorHandler, #type:ignore[dict-item]
                                                                                 NotFoundException:handle_404_error} #type:ignore[dict-item]
    def add_exception_handler(
        self,
        exc_class_or_status_code: typing.Union[int , type[Exception]],
        handler: ExceptionHandlerType,
    ) -> None:
        if isinstance(exc_class_or_status_code, int):
            self._status_handlers[exc_class_or_status_code] = handler
        else:
            assert issubclass(exc_class_or_status_code, Exception)
            self._exception_handlers[exc_class_or_status_code] = handler #type:ignore

    async def __call__(self, request: Request,response :Response,call_next :typing.Callable[...,typing.Awaitable[None]],) -> Response:


        return await wrap_app_handling_exceptions(
            request=request,
            response=response,
            call_next=call_next,
            exception_handlers=self._exception_handlers,
            status_handlers=self._status_handlers
            
            
        )

    async def http_exception(self, request: Request,response:Response, exc: HTTPException) -> typing.Any :
        assert isinstance(exc, HTTPException)
        if exc.status_code in {204, 304}: #type:ignore
            return response.empty(status_code=exc.status_code, headers=exc.headers)
        return response.text(exc.detail, status_code=exc.status_code, headers=exc.headers)

