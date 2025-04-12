from functools import wraps
from typing import Optional, Dict, List, Type, Union, Awaitable
from uuid import uuid4
from pydantic import BaseModel
from inspect import signature, getdoc
from typing import get_type_hints, get_origin, get_args
from nexios.application import NexiosApp
from nexios.http import Request, Response
from .config import OpenAPIConfig
from .models import (
    Parameter,
    ExternalDocumentation,
    RequestBody,
    MediaType,
    Response as OpenAPIResponse,
    Operation,
    Schema,
    PathItem,
)


class APIDocumentation:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self, app: Optional[NexiosApp] = None, config: Optional[OpenAPIConfig] = None
    ):
        self.app = app
        self.config = config or OpenAPIConfig()
        if app:
            self._setup_doc_routes()

    def _setup_doc_routes(self):
        """Set up routes for serving OpenAPI specification"""

        @self.app.get("/openapi.json", exclude_from_schema=True)  # type:ignore
        async def serve_openapi(request: Request, response: Response):
            openapi_json = self.config.openapi_spec.model_dump(
                by_alias=True, exclude_none=True
            )
            return response.json(openapi_json)

        @self.app.get("/docs", exclude_from_schema=True)  # type:ignore
        async def swagger_ui(request: Request, response: Response):
            return response.html(self._generate_swagger_ui())

    @classmethod
    def get_instance(cls):
        return cls._instance

    def _generate_swagger_ui(self) -> str:
        """Generate Swagger UI HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.config.openapi_spec.info.title} - Docs</title>
            <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4.18.3/swagger-ui.css">
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
            <script>
                window.onload = function() {{
                    SwaggerUIBundle({{
                        url: '/openapi.json',
                        dom_id: '#swagger-ui',
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIBundle.SwaggerUIStandalonePreset
                        ],
                        layout: "BaseLayout"
                    }});
                }}
            </script>
        </body>
        </html>
        """

    def document_endpoint(
        self,
        path: str,
        method: str,
        summary: str = "",
        description: Optional[str] = None,
        parameters: Optional[List[Parameter]] = None,
        request_body: Optional[Type[BaseModel]] = None,
        responses: Optional[Union[BaseModel, Dict[int, BaseModel]]] = None,
        tags: Optional[List[str]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
        operation_id: Optional[str] = None,
        deprecated: bool = False,
        external_docs: Optional[ExternalDocumentation] = None,
    ):
        """
        Decorator to document API endpoints with OpenAPI specification

        :param path: URL path of the endpoint
        :param method: HTTP method (get, post, put, delete, etc.)
        :param summary: Short summary of the endpoint
        :param description: Detailed description of the endpoint
        :param parameters: List of parameters
        :param request_body: Pydantic model for request body
        :param responses: Response model(s)
        :param tags: Categorization tags for the endpoint
        :param security: Security requirements
        :param operation_id: Unique identifier for the operation
        :param deprecated: Whether the endpoint is deprecated
        :param external_docs: External documentation reference
        """

        def decorator(func):
            # Prepare request body specification
            request_body_spec = None
            if request_body:
                request_body_spec = RequestBody(
                    content={
                        "application/json": MediaType(  # type:ignore
                            schema=Schema(  # type:ignore
                                **request_body.model_json_schema()
                            )
                        )
                    }
                )
            else:
                if method not in ["GET"]:
                    request_body_spec = RequestBody(
                        content={
                            "application/json": MediaType(  # type:ignore
                                schema=Schema()  # type:ignore
                            )
                        }
                    )

            # Prepare responses specification
            responses_spec = {}
            if responses:
                # Single model case (default to 200 OK)
                if isinstance(responses, type) and issubclass(responses, BaseModel):
                    responses_spec["200"] = OpenAPIResponse(
                        description="Successful Response",
                        content={
                            "application/json": MediaType(  # type:ignore
                                schema=Schema(  # type:ignore
                                    **responses.model_json_schema()
                                )
                            )
                        },
                    )
                # Handle List[Model] case
                elif hasattr(responses, "__origin__") and responses.__origin__ is list:
                    item_model = responses.__args__[0]
                    if issubclass(item_model, BaseModel):
                        responses_spec["200"] = OpenAPIResponse(
                            description="Successful Response",
                            content={
                                "application/json": MediaType(  # type:ignore
                                    schema=Schema(  # type:ignore
                                        type="array",
                                        items=Schema(**item_model.model_json_schema()),
                                    )
                                )
                            },
                        )
                # Multiple responses case
                elif isinstance(responses, dict):
                    for status_code, model in responses.items():
                        # Handle direct model
                        if isinstance(model, type) and issubclass(model, BaseModel):
                            responses_spec[str(status_code)] = OpenAPIResponse(
                                description=f"Response for status code {status_code}",
                                content={
                                    "application/json": MediaType(  # type:ignore
                                        schema=Schema(  # type:ignore
                                            **model.model_json_schema()
                                        )
                                    )
                                },
                            )
                        # Handle List[Model]
                        elif hasattr(model, "__origin__") and model.__origin__ is list:
                            item_model = model.__args__[0]
                            if issubclass(item_model, BaseModel):
                                responses_spec[str(status_code)] = OpenAPIResponse(
                                    description=f"Response for status code {status_code}",
                                    content={
                                        "application/json": MediaType(  # type:ignore
                                            schema=Schema(  # type:ignore
                                                type="array",
                                                items=Schema(
                                                    **item_model.model_json_schema()
                                                ),
                                            )
                                        )
                                    },
                                )
            else:
                # Default response if no responses specified
                responses_spec["200"] = OpenAPIResponse(
                    description="Successful Response"
                )

            operation = Operation(
                summary=summary,
                description=description,
                responses=responses_spec,
                tags=tags,
                parameters=parameters or [],  # type:ignore
                requestBody=request_body_spec,
                security=security,
                operationId=operation_id or str(uuid4()),
                deprecated=deprecated,
                externalDocs=external_docs,
            )

            # Add operation to the OpenAPI specification
            if path not in self.config.openapi_spec.paths:
                self.config.openapi_spec.paths[path] = PathItem()

            setattr(self.config.openapi_spec.paths[path], method.lower(), operation)

            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            return wrapper

        return decorator
