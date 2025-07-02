# Nexios Framework: OpenAPI Authentication Guide

Nexios supports OpenAPI authentication, which allows you to secure your API endpoints with JSON Web Tokens (JWT) or other authentication mechanisms. Here's how you can set up OpenAPI authentication in your Nexios application 

## basic setup

By default already provide `bearerAuth` in OpenAPI documentation .

```python
from nexios import NexiosApp
app = NexiosApp()

@app.get("/", security=[{"bearerAuth": []}])
async def get_root(req, res):
    return {"message": "Hello, world!"}
```

<img src="./bearerAuth.png">

## Adding Multi  Security Schemes

```python
from nexios import NexiosApp
app = NexiosApp()

@app.get("/", security=[{"bearerAuth": []}, {"apiKey": []}])
async def get_root(req, res):
    return {"message": "Hello, world!"}
```
::: warning ⚠️ Warning
You most register security scheme before using it.
:::
## Registering Security Schemes
::: tip 💡Tip
You can also access the openapi config from `app.docs.cofig` object.
:::

```python
from nexios.openapi.models import  APIKey

app.docs.add_security_scheme(
    "apiKeyAuth",
    APIKey(
    name="X-API-KEY",
    **{
        "in": "header",
        "description": "My API key",
        "type": "apiKey"
    }
)
)
```

::: warning ⚠️ Warning

Note : The dict used indead of passing the argugument directly. because `in` is a reserved keyword in python.

:::

### Authentication Types

JWT Bearer Authentication
The most common method for modern APIs. Clients include a token in the Authorization header.

```python 
app.docs.config.add_security_scheme(
    "jwtAuth",  # Unique identifier
    HTTPBearer(
        type="http",
        scheme="bearer",
        bearerFormat="JWT",
        description="Requires valid JWT token in Authorization header"
    )
)

```

### API Key Authentication
For simpler authentication needs, using keys in headers, queries, or cookies.

```python
app.docs.config.add_security_scheme(
    "apiKeyAuth",
    APIKey(
        name="X-API-KEY",  # Header/parameter name
        **{
            "in": "header",  # Can be "header", "query", or "cookie"
            "description": "Access with your API key"
        }
    )
)
```

## OAuth2 Authentication

```py
app.docs.config.add_security_scheme(
    "oauth2",
    OAuth2(
        flows=OAuthFlows(
            password=OAuthFlowPassword(
                tokenUrl="/auth/token",
                scopes={
                    "read": "Read access",
                    "write": " Write access",
                    "admin": " Admin privileges"
                }
            )
        ),
        description="OAuth2 password flow authentication"
    )
)
```



## OAuth2 Scoped Routes
Require specific permissions:



```python
from nexios import NexiosApp
app = NexiosApp()

@app.get("/", security=[{"oauth2": ["read"]}])
async def get_root(req, res):
    return {"message": "Hello, world!"}
```