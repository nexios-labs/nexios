from functools import wraps
from typing import Optional, Dict, List, Union, Any
from pydantic import BaseModel
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
    Path  # Import the specific Path parameter class
)

class APIDocumentation:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self, 
        app: NexiosApp, 
        config: Optional[OpenAPIConfig] = None
    ):
        self.app = app 
        self.config = config or OpenAPIConfig()
        self._setup_doc_routes()
    
    def _setup_doc_routes(self):
        """Set up routes for serving OpenAPI specification"""
        @self.app.route("/openapi.json", methods=["GET"])
        async def serve_openapi(request: Request, response: Response):
            return response.json(
                self.config.openapi_spec.model_dump(by_alias=True, exclude_unset=True)
            )
        
        @self.app.route("/docs", methods=["GET"])
        async def swagger_ui(request: Request, response: Response):
            return response.html(self._generate_swagger_ui())
    
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
            <script src="https://unpkg.com/swagger-ui-dist@4.18.3/swagger-ui-bundle.js"></script>
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
    
    def _extract_path_parameters(self, path: str) -> List[str]:
        """Extract parameter names from path pattern like '/items/{item_id}'"""
        return [segment[1:-1] for segment in path.split("/") 
                if segment.startswith("{") and segment.endswith("}")]

    def _create_path_parameter(self, param_name: str) -> Path:
        """Create a Path parameter with proper OpenAPI fields"""
        return Path(
            name=param_name,
            description=f"{param_name} parameter",
            required=True,
            schema=Schema(type="string")  # Default to string type
        )

    def _prepare_parameters(
        self,
        path: str,
        explicit_parameters: Optional[List[Parameter]] = None
    ) -> Optional[List[Parameter]]:
        """Combine explicit parameters with auto-detected path parameters"""
        all_parameters = []
        
        # Add explicit parameters if provided
        if explicit_parameters:
            all_parameters.extend(explicit_parameters)
        
        # Auto-detect and add path parameters
        path_params = self._extract_path_parameters(path)
        for param in path_params:
            if not any(p.name == param for p in all_parameters):
                all_parameters.append(self._create_path_parameter(param))
        
        return all_parameters or None

    def _prepare_request_body(
        self, 
        request_body: Optional[BaseModel]
    ) -> Optional[RequestBody]:
        """Prepare request body specification with MediaType"""
        if not request_body:
            return None
            
        return RequestBody(
            content={
                "application/json": MediaType(
                    schema=Schema(**request_body.model_json_schema())
                )
            }
        )

    def _prepare_responses(
        self,
        responses: Optional[Union[BaseModel, Dict[int, BaseModel]]]
    ) -> Dict[str, OpenAPIResponse]:
        """Prepare responses specification with proper MediaType handling"""
        responses_spec = {}
        
        if not responses:
            # Default response if none specified
            responses_spec["200"] = OpenAPIResponse(
                description="Successful Response"
            )
        elif isinstance(responses, BaseModel):
            # Single response model case (default to 200 OK)
            responses_spec["200"] = OpenAPIResponse(
                description="Successful Response",
                content={
                    "application/json": MediaType(
                        schema=Schema(**responses.model_json_schema())
            )}
            )
        elif isinstance(responses, dict):
            # Multiple responses case
            for status_code, model in responses.items():
                responses_spec[str(status_code)] = OpenAPIResponse(
                    description=f"Response for status code {status_code}",
                    content={
                        "application/json": MediaType(
                            schema=Schema(**model.model_json_schema())
                )}
                )
        
        return responses_spec

    def document_endpoint(
        self,
        path: str,
        method: str,
        summary: str = "",
        description: Optional[str] = None,
        parameters: Optional[List[Parameter]] = None,
        request_body: Optional[BaseModel] = None,
        responses: Optional[Union[BaseModel, Dict[int, BaseModel]]] = None,
        tags: Optional[List[str]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
        operation_id: Optional[str] = None,
        deprecated: bool = False,
        external_docs: Optional[ExternalDocumentation] = None
    ) -> callable:
        """
        Decorator to document API endpoints with OpenAPI specification
        
        Args:
            path: URL path pattern (may include parameters like '/items/{id}')
            method: HTTP method (get, post, put, delete, etc.)
            summary: Short summary of the endpoint
            description: Detailed description
            parameters: Explicit list of parameters
            request_body: Pydantic model for request body
            responses: Response model(s) as either single model or status-code mapped dict
            tags: Categorization tags
            security: Security requirements
            operation_id: Unique operation identifier
            deprecated: Mark endpoint as deprecated
            external_docs: External documentation reference
        """
        def decorator(func: callable) -> callable:
            # Prepare all components
            final_parameters = self._prepare_parameters(path, parameters)
            request_body_spec = self._prepare_request_body(request_body)
            responses_spec = self._prepare_responses(responses)

            # Create OpenAPI Operation
            operation = Operation(
                summary=summary,
                description=description,
                responses=responses_spec,
                tags=tags or [],
                parameters=final_parameters,
                requestBody=request_body_spec,
                security=security,
                operationId=operation_id or func.__name__,
                deprecated=deprecated,
                externalDocs=external_docs
            )

            # Add to OpenAPI spec
            if path not in self.config.openapi_spec.paths:
                self.config.openapi_spec.paths[path] = PathItem()
            
            setattr(
                self.config.openapi_spec.paths[path], 
                method.lower(), 
                operation
            )
            
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator