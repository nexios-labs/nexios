from nexios.validator import ValidationError, Schema #type:ignore
from functools import wraps
from typing import Callable, Any, Optional, Awaitable
from typing_extensions import Annotated
from nexios.http import Request,Response

def validate_request(
    schema: Annotated[Schema, "The schema instance for validation"], 
    fail_silently: Annotated[bool, "If True, suppresses validation errors"] = False,
    error_handler: Optional[Callable[[Any, Any,Any], Awaitable[None]]] = None
) -> Annotated[Callable[[Any, Any, Any, Any], Any], "Decorator for request validation"]:
    """
    Decorator to validate incoming requests (JSON, FormData, URL-Encoded) using the provided schema.

    Args:
        schema (Schema): The schema instance for validation.
        fail_silently (bool, optional): If True, suppresses validation errors. Defaults to False.
        error_handler (Optional[Callable]): An optional async function to handle validation errors.

    Returns:
        Callable: A decorated async function that validates request data before processing.
    """
    def decorator(handler: Callable[[Any, Any, Any, Any], Awaitable[Any]]) -> Callable[[Any, Any, Any, Any], Awaitable[Any]]:
        @wraps(handler)
        async def wrapper(request: Request, response: Response, *args: Any, **kwargs: Any) -> Any:
            """
            Validates the request data and attaches the validated data or validation error.

            Args:
                request (Any): The incoming request object.
                response (Any): The response object.

            Returns:
                Any: The result of the handler function.
            """
            try:
                content_type = request.content_type
                
                if "application/json" == content_type:
                    data = await request.json
                elif "multipart/form-data" == content_type or "application/x-www-form-urlencoded" == content_type:
                    data :Any = await request.form_data
                else:
                    data = {}

                request.validated_data = schema.load(data) #type:ignore
                request.validation_error = None   #type:ignore
            
            except ValidationError as err:
                request.validation_error = err.messages # type: ignore 

                if error_handler:
                    await error_handler(request, response, err)

                if not fail_silently:
                    raise err

            return await handler(request, response, *args, **kwargs)

        return wrapper
    return decorator # type: ignore 
