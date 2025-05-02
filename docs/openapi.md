---
icon: file-doc
---

# OpenAPI

Nexios provides built-in support for generating OpenAPI documentation (formerly known as Swagger) for your API. This allows you to create interactive API documentation that helps developers understand your endpoints, request/response models, and authentication requirements.

## Basic Setup

By default, Nexios automatically generates OpenAPI documentation for all your routes. The documentation is accessible at `/docs` and the raw OpenAPI specification is available at `/openapi.json`:

```python
from nexios import get_application

app = get_application()

@app.get("/users")
async def get_users(req, res):
    """List all users"""
    return res.json([{"id": 1, "name": "John"}])

@app.get("/users/{user_id}")
async def get_user(req, res):
    """Get a specific user by ID"""
    user_id = req.path_params.user_id
    return res.json({"id": user_id, "name": "John"})
```

With this simple setup, Nexios will generate basic documentation for your routes. However, to create truly comprehensive API documentation, you'll want to add more details.

## Documenting Response Models with Pydantic

Nexios integrates seamlessly with Pydantic to document your API's request and response models. This allows for automatic schema generation and validation:

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from nexios import get_application

app = get_application()

# Define Pydantic models
class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True
    
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

# Document the endpoint with response model
@app.get("/users", responses=List[User], tags=["users"])
async def get_users(req, res):
    """
    List all users in the system
    
    Returns a list of user objects
    """
    users = [
        {"id": 1, "name": "John", "email": "john@example.com"},
        {"id": 2, "name": "Jane", "email": "jane@example.com"}
    ]
    return res.json(users)

# Document the endpoint with request and response models
@app.post("/users", responses=User, request_model=UserCreate, tags=["users"])
async def create_user(req, res):
    """
    Create a new user
    
    Takes user creation data and returns the created user
    """
    data = await req.json
    # Process data (validation is automatic)
    new_user = {"id": 3, **data, "password": "***hidden***"}
    return res.json(new_user)
```

## Complex Response Schemas

For more complex API responses, Nexios allows you to document nested models, relationships, and various response types:

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union, Any
from datetime import datetime
from uuid import UUID
from nexios import get_application

app = get_application()

# Define complex nested models
class Address(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str = "USA"

class Role(BaseModel):
    name: str
    permissions: List[str]

class UserProfile(BaseModel):
    biography: Optional[str] = None
    avatar_url: Optional[str] = None
    social_links: Dict[str, str] = {}

class User(BaseModel):
    id: UUID
    username: str
    email: str
    roles: List[Role]
    addresses: List[Address]
    profile: UserProfile
    created_at: datetime
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

# Define error responses
class ErrorResponse(BaseModel):
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None

# Document endpoint with multiple possible responses
@app.get(
    "/users/{user_id}",
    responses={
        200: User,
        404: ErrorResponse,
        500: ErrorResponse
    },
    tags=["users"]
)
async def get_user_details(req, res):
    """
    Get detailed user information
    
    Returns comprehensive user data including profile, roles, and addresses
    """
    user_id = req.path_params.user_id
    
    # Example error handling that would be documented
    if user_id == "invalid":
        return res.json(
            {"code": 404, "message": "User not found"},
            status_code=404
        )
    
    # Return sample user data
    return res.json({
        "id": user_id,
        "username": "johndoe",
        "email": "john@example.com",
        "roles": [{"name": "admin", "permissions": ["read", "write", "delete"]}],
        "addresses": [
            {
                "street": "123 Main St",
                "city": "Boston",
                "state": "MA",
                "postal_code": "02101",
                "country": "USA"
            }
        ],
        "profile": {
            "biography": "Software developer",
            "avatar_url": "https://example.com/avatar.jpg",
            "social_links": {"twitter": "https://twitter.com/johndoe"}
        },
        "created_at": "2023-01-01T00:00:00Z",
        "last_login": "2023-06-15T14:22:10Z",
        "metadata": {"preferences": {"theme": "dark"}}
    })
```

## Generic Response Types

Nexios also handles generic response types like paginated results:

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Generic, TypeVar
from nexios import get_application

app = get_application()

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    next_page: Optional[int] = None
    prev_page: Optional[int] = None

class Product(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None

@app.get("/products", responses=PaginatedResponse[Product], tags=["products"])
async def list_products(req, res):
    """
    List products with pagination
    
    Returns a paginated list of products
    """
    # Get pagination parameters
    page = int(req.query_params.get("page", "1"))
    page_size = int(req.query_params.get("page_size", "10"))
    
    # Example data
    products = [
        {"id": i, "name": f"Product {i}", "price": 10.99 * i}
        for i in range(1, 21)
    ]
    
    # Calculate pagination
    start = (page - 1) * page_size
    end = start + page_size
    page_items = products[start:end]
    total = len(products)
    
    # Build response
    response = {
        "items": page_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "next_page": page + 1 if end < total else None,
        "prev_page": page - 1 if page > 1 else None
    }
    
    return res.json(response)
```

## Customizing OpenAPI Configuration

You can customize the OpenAPI configuration to provide more information about your API:

```python
from nexios import get_application
from nexios.openapi import OpenAPIConfig

app = get_application()

# Customize OpenAPI configuration
app.config.openapi = OpenAPIConfig(
    title="My Awesome API",
    description="This API provides access to awesome features",
    version="1.0.0",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "https://example.com/support",
        "email": "support@example.com"
    },
    license={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
    },
    servers=[
        {"url": "https://api.example.com/v1", "description": "Production server"},
        {"url": "https://staging-api.example.com/v1", "description": "Staging server"},
        {"url": "http://localhost:8000", "description": "Development server"}
    ],
    # Additional OpenAPI specification fields can be added here
)
```

## Authentication Documentation

Documenting authentication requirements is crucial for API users. Nexios allows you to specify security schemes and requirements:

```python
from nexios import get_application
from nexios.openapi import OpenAPIConfig

app = get_application()

# Configure OpenAPI with authentication
app.config.openapi = OpenAPIConfig(
    title="Secure API",
    version="1.0.0",
    # Define security schemes
    security_schemes={
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        },
        "apiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-KEY"
        },
        "oauth2Auth": {
            "type": "oauth2",
            "flows": {
                "implicit": {
                    "authorizationUrl": "https://example.com/oauth/authorize",
                    "scopes": {
                        "read:users": "Read user information",
                        "write:users": "Modify user information"
                    }
                }
            }
        }
    },
    # Define global security requirement (applied to all endpoints)
    security=[
        {"bearerAuth": []}
    ]
)

# Routes with specific security requirements
@app.get(
    "/public/info",
    security=[],  # Override global security - no auth required
    tags=["public"]
)
async def public_info(req, res):
    """This endpoint is publicly accessible"""
    return res.json({"message": "Public info"})

@app.get(
    "/admin/settings",
    security=[{"bearerAuth": []}, {"apiKeyAuth": []}],  # Requires either JWT or API key
    tags=["admin"]
)
async def admin_settings(req, res):
    """This endpoint requires admin authentication"""
    return res.json({"message": "Admin settings"})

@app.get(
    "/users/profile",
    security=[{"oauth2Auth": ["read:users"]}],  # Requires OAuth2 with specific scope
    tags=["users"]
)
async def user_profile(req, res):
    """This endpoint requires OAuth2 authentication with read:users scope"""
    return res.json({"message": "User profile"})
```

## Customizing Swagger UI

Nexios allows you to customize the appearance and behavior of Swagger UI:

```python
from nexios import get_application
from nexios.openapi import OpenAPIConfig

app = get_application()

# Customize Swagger UI
app.config.openapi = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    swagger_ui_config={
        "deepLinking": True,
        "displayOperationId": True,
        "defaultModelsExpandDepth": 3,
        "defaultModelExpandDepth": 3,
        "defaultModelRendering": "example",
        "displayRequestDuration": True,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "syntaxHighlight": {
            "activate": True,
            "theme": "monokai"
        },
        "tryItOutEnabled": True
    },
    # Custom CSS URL to style Swagger UI
    swagger_ui_css="https://cdn.example.com/custom-swagger.css"
)
```

For a completely custom UI, you can override the default Swagger UI template:

```python
from nexios import get_application
from nexios.openapi import APIDocumentation

app = get_application()

# Get the API documentation instance
api_docs = APIDocumentation.get_instance()

# Replace the _generate_swagger_ui method to customize the HTML
def custom_swagger_ui() -> str:
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Custom API Documentation</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4.18.3/swagger-ui.css">
        <link rel="stylesheet" href="/custom/styles.css">
        <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
    </head>
    <body>
        <header>
            <h1>My Company API</h1>
            <p>API Version 1.0</p>
        </header>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                SwaggerUIBundle({
                    url: '/openapi.json',
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout",
                    deepLinking: true,
                    syntaxHighlight: {
                        theme: 'monokai'
                    },
                    oauth2RedirectUrl: window.location.origin + '/oauth2-redirect.html',
                    tagsSorter: 'alpha',
                    operationsSorter: 'alpha',
                    persistAuthorization: true
                });
            }
        </script>
        <footer>
            <p>© 2025 My Company - <a href="/terms">Terms of Service</a></p>
        </footer>
    </body>
    </html>
    """

# Replace the method
api_docs._generate_swagger_ui = custom_swagger_ui
```

## Advanced Usage: Manual Documentation

In some cases, you might need finer control over your API documentation. Nexios allows you to manually document endpoints:

````python
from nexios import get_application
from nexios.openapi import APIDocumentation, Parameter, Schema, ExternalDocumentation
from pydantic import BaseModel

app = get_application()
api_docs = APIDocumentation.get_instance()

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str

# This route won't be automatically documented
@app.get("/items/{item_id}", exclude_from_schema=True)
async def get_item(req, res):
    item_id = req.path_params.item_id
    return res.json({"id": item_id, "name": "Item", "description": "An item"})

# Manually document the route
@api_docs.document_endpoint(
    path="/items/{item_id}",
    method="get",
    summary="Get an item by ID",
    description="Retrieves detailed information about a specific item",
    parameters=[
        Parameter(
            name="item_id",
            in_="path",
            required=True,
            schema=Schema(type="integer"),
            description="The unique identifier

---
icon: file-doc
---

# OpenApi

The OpenAPI documentation is automatically set up when you create a Nexios app. The documentation is available at:

- `/openapi.json` - The OpenAPI specification in JSON format
- `/docs` - Interactive Swagger UI documentation

### Documenting Routes

When you define routes using the standard decorators (`@app.get`, `@app.post`, etc.), the OpenAPI documentation is automatically generated based on the route parameters you provide.

#### Example Route with Documentation

```python
from pydantic import BaseModel
from nexios import get_application

app = get_application()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

@app.post(
    "/users",
    summary="Create a new user",
    description="Creates a new user with the provided details",
    request_model=UserCreate,
    responses={200: UserResponse, 400: {"description": "Invalid input"}},
    tags=["Users"],
    security=[{"bearerAuth": []}],
    operation_id="createUser"
)
async def create_user(request: Request, response: Response):
    # Your route logic here
    user_data = await request.json()
    # ... process user creation
    return response.json({"id": 1, "username": user_data["username"], "email": user_data["email"]})
````

#### Route Documentation Parameters

All route decorators (`get`, `post`, `put`, etc.) accept the following documentation parameters:

* `summary`: Short summary of the endpoint
* `description`: Detailed description of the endpoint
* `request_model`: Pydantic model for the request body
* `responses`: Dictionary mapping status codes to response models or descriptions
* `tags`: List of tags for grouping endpoints
* `security`: Security requirements for the endpoint
* `operation_id`: Unique identifier for the operation
* `deprecated`: Mark endpoint as deprecated (True/False)
* `parameters`: List of `Parameter` objects for path/query parameters
* `exclude_from_schema`: Exclude endpoint from OpenAPI docs (True/False)

### Path Parameters

Path parameters are automatically detected from your route path and documented. For example:

```python
@app.get(
    "/users/{user_id}",
    summary="Get user by ID",
    responses={200: UserResponse, 404: {"description": "User not found"}},
    tags=["Users"]
)
async def get_user(request: Request, response: Response, user_id: int):
    # Your route logic here
```

### Query Parameters

For query parameters, you can define them using the `parameters` argument:

```python
from nexios.openapi.models import Query

@app.get(
    "/users",
    summary="List users",
    parameters=[
        Query(name="page", description="Page number", required=False, schema=Schema(type="integer")),
        Query(name="limit", description="Items per page", required=False, schema=Schema(type="integer"))
    ],
    tags=["Users"]
)
async def list_users(request: Request, response: Response):
    # Your route logic here
```

### Security Schemes

The default configuration includes a bearer token security scheme. You can add additional security schemes using:

```python
from nexios.openapi.models import APIKey

# Add an API key security scheme
app.openapi_config.add_security_scheme(
    "apiKey",
    APIKey(name="X-API-Key", in_="header")
)
```

Then reference it in your route:

```python
@app.get(
    "/secure-data",
    security=[{"apiKey": []}],
    summary="Get secure data"
)
async def get_secure_data(request: Request, response: Response):
    # Your route logic here
```

### Customizing OpenAPI Config

You can customize the OpenAPI configuration when creating your app:

```python
from nexios.openapi.models import Contact, License

config = MakeConfig(
    "openapi":{
        "title":"My API",
        "version":"1.0.0",
        "description":"API for my awesome application",
        "contact":Contact(name="API Support", email="support@example.com"),
        "license":License(name="MIT", url="https://opensource.org/licenses/MIT")
    }
)

app = get_application(config=config)
```

### Excluding Routes from Documentation

To exclude a route from the OpenAPI documentation:

```python
@app.get("/internal/metrics", exclude_from_schema=True)
async def get_metrics(request: Request, response: Response):
    # Internal route not shown in docs
```

### Viewing Documentation

After setting up your routes, you can view the documentation at:

1. Swagger UI: `http://localhost:8000/docs`
2. OpenAPI JSON: `http://localhost:8000/openapi.json`
