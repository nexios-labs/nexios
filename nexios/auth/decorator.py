from nexios.decorators import RouteDecorator 
import typing
from .exceptions import AuthenticationFailed
from nexios.http import Request, Response

class auth(RouteDecorator):
    
    def __init__(self, scopes :typing.List[str]):
        super().__init__()
        self.scopes = scopes
        
        
    def __call__(self, handler: typing.Callable[..., typing.Awaitable[typing.Any]]) -> typing.Any:
        async def wrapper(*args: typing.List[typing.Any], **kwargs: typing.Dict[str, typing.Any]) -> typing.Any:
            *_, request, response = args  # Ensure request and response are last
            
            if not isinstance(request, Request) or not isinstance(response, Response):
                raise TypeError("Expected request and response as the last arguments")

            if not request.scope.get("user"):
                
                raise AuthenticationFailed
            
            user, scope  = request.scope.get("user") #type:ignore
            if self.scopes and scope not in self.scopes:
                raise AuthenticationFailed
            
            
            return await handler(request, response)
        return wrapper 