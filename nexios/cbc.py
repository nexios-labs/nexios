from nexios.http import response, request
from nexios.http.response import NexiosResponse
from nexios.types import HandlerType
from typing import Any,Union


class APIHandler:
    async def handle_error(
        self,
        error: Exception,
        request: request.Request,
        response: response.NexiosResponse,
    ):
        pass

    async def before_request(
        self, request: request.Request, response: response.NexiosResponse
    ):
        pass

    async def after_request(
        self, request: request.Request, response: response.NexiosResponse
    ):
        """Hook that runs after each request"""

    async def __call__(
        self, request: request.Request, response: response.NexiosResponse
    ) -> Any:
        method = request.method.lower()
        handler: Union[HandlerType, None] = getattr(self, method, None)
        if not callable(handler):
            return response.text("Method not allowed", status_code=405)

        try:
            before_request = await self.before_request(request, response)
            if isinstance(before_request, NexiosResponse):  # type:ignore
                return before_request

            _response: HandlerType = await handler(request, response)  # type:ignore
            await self.after_request(request, response)

            return _response

        except Exception as e:
            await self.handle_error(e, request, response)
