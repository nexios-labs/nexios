from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from nexios.openapi.models import Parameter


def mark_as_route(
    path: str,
    methods: List[str] = ["get", "post", "patch", "put", "delete"],
    name: Optional[str] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    responses: Optional[Dict[int, Any]] = None,
    request_model: Optional[Type[BaseModel]] = None,
    middleware: List[Any] = [],
    tags: Optional[List[str]] = None,
    security: Optional[List[Dict[str, List[str]]]] = None,
    operation_id: Optional[str] = None,
    deprecated: bool = False,
    parameters: List[Parameter] = [],
    exclude_from_schema: bool = False,
):
    def decorator(func):
        # Use setattr to set attributes dynamically
        setattr(func, "_is_route", True)
        setattr(func, "_path", path)
        setattr(func, "_allowed_methods", [method.lower() for method in methods])
        setattr(func, "_name", name or func.__name__)
        setattr(func, "_summary", summary or "")
        setattr(func, "_description", description or "")
        setattr(func, "_responses", responses or {})
        setattr(func, "_request_model", request_model)
        setattr(func, "_middleware", middleware)
        setattr(func, "_tags", tags or [])
        setattr(func, "_security", security or [])
        setattr(func, "_operation_id", operation_id or func.__name__)
        setattr(func, "_deprecated", deprecated)
        setattr(func, "_parameters", parameters)
        setattr(func, "_exclude_from_schema", exclude_from_schema)

        return func

    return decorator
