The OpenAPI documentation is automatically set up when you create a Nexios app. The documentation is available at:

- `/openapi.json` - The OpenAPI specification in JSON format
- `/docs` - Interactive Swagger UI documentation

## Documenting Routes

When you define routes using the standard decorators (`@app.get`, `@app.post`, etc.), the OpenAPI documentation is automatically generated based on the route parameters you provide.

### Example Route with Documentation

```python
from pydantic import BaseModel
from nexios import NexiosApp

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
```

### Route Documentation Parameters

All route decorators (`get`, `post`, `put`, etc.) accept the following documentation parameters:

- `summary`: Short summary of the endpoint
- `description`: Detailed description of the endpoint
- `request_model`: Pydantic model for the request body
- `responses`: Dictionary mapping status codes to response models or descriptions
- `tags`: List of tags for grouping endpoints
- `security`: Security requirements for the endpoint
- `operation_id`: Unique identifier for the operation
- `deprecated`: Mark endpoint as deprecated (True/False)
- `parameters`: List of `Parameter` objects for path/query parameters
- `exclude_from_schema`: Exclude endpoint from OpenAPI docs (True/False)

## Path Parameters

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

## Query Parameters

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

## Security Schemes

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

## Customizing OpenAPI Config

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

app = NexiosApp(config=config)
```

## Excluding Routes from Documentation

To exclude a route from the OpenAPI documentation:

```python
@app.get("/internal/metrics", exclude_from_schema=True)
async def get_metrics(request: Request, response: Response):
    # Internal route not shown in docs
```

## Viewing Documentation

After setting up your routes, you can view the documentation at:

1. Swagger UI: `http://localhost:8000/docs`
2. OpenAPI JSON: `http://localhost:8000/openapi.json`
