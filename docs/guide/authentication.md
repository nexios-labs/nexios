---
title: Authentication in Nexios
description: A guide to authentication in Nexios
head:
  - - meta
    - property: og:title
      content: Authentication in Nexios
  - - meta
    - property: og:description
      content: Nexios makes authentication simple yet powerful. Learn how to secure your API with just one line of code, and discover the built-in features that make authentication a breeze.
---

# Authentication in Nexios
Nexios provides a simple yet powerful authentication system that makes securing your API a breeze. With just one line of code, you can protect your routes with robust authentication logic.

By default, Nexios will try to authenticate users with a provided list of `backends`. This means that users can authenticate with either JSON Web Tokens (JWT) or session-based authentication. You can also add custom backends to support other authentication methods, such as API keys or OAuth.

## The Basic Idea

Nexios uses a simple yet powerful authentication system that makes securing your API a breeze. With just one line of code, you can protect your routes with robust authentication logic.

```py
from nexios import NexiosApp
from nexios.config import MakeConfig
from nexios.http import Request, Response
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.auth.backends.jwt import JWTAuthBackend
from nexios.auth import SimpleUser

app = NexiosApp(config=MakeConfig(
    secret_key="your-secret-key",
    
))
app.add_middleware(AuthenticationMiddleware(
    user_model=SimpleUser,
    backend=JWTAuthBackend()
))

@app.get("/profile")
@auth()
async def user_profile(request: Request, response: Response):
    return {
        "message": f"Welcome back, {request.user.display_name}!",
        "user_id": request.user.identity,
        "is_authenticated": request.user.is_authenticated
    }
```

::: tip
the `user_model` is the model that will be used to load the user from the authentication backend.
:::

## Authentication Middleware
The `AuthenticationMiddleware` takes the following arguments:

- `user_model`: The user model class that will be used to load the user from the authentication backend.
- `backend`: The authentication backend class that will be used to authenticate the user.
- `backends`: A list of authentication backend classes that will be used to authenticate the user. The first backend that successfully authenticates the user will be used.

The middleware will then attach the user to the request object under the `request.user` attribute. If the user is not authenticated, the middleware will attach an `UnauthenticatedUser` to the request object.

The middleware will also attach the authentication type to the request object under the `request.scope["auth"]` attribute. This allows you to check the authentication type in your route handlers.

::: tip
nexios provides a built-in `SimpleUser` class that you can use as the `user_model` argument.
:::


## User Model

The user model is responsible for loading the user from the authentication backend. Nexios provides a simple `BaseUser` class that you can extend to create your own user model.

Here's an example of how to extend the `BaseUser` class to include a `last_login_ip` field:

```python
from nexios.auth.base import BaseUser

class User(BaseUser):
   def __init__(self, identity: str, display_name: str, last_login_ip: str):
       self.identity = identity
       self.display_name = display_name
       self.last_login_ip = last_login_ip

   @property
   def is_authenticated(self) -> bool:
       return True

   @property
   def display_name(self) -> str:
       return self.display_name

   @property
   def identity(self) -> str:
       return self.identity

   @property
   def last_login_ip(self) -> str:
       return self.last_login_ip


    @classmethod
    async def load_user(cls, identity: str) -> User:
        
        user = db.get_user_by_id(identity)
        if user:
            return cls(
                identity=user.id,
                display_name=user.display_name,
                last_login_ip=user.last_login_ip
            )
        return None

app.add_middleware(AuthenticationMiddleware(
    user_model=User,
    backend=JWTAuthBackend()
))

```

- `load_user` is a class method that is responsible for loading the user from the authentication backend it can be from a database or any other source.
now you can access the user via `request.user` and the authentication type via `request.scope["auth"]` if the user is authenticated.

::

## JWT Authentication Backend
Nexios provides a built-in `JWTAuthBackend` that you can use to authenticate users with JSON Web Tokens (JWT).

The `JWTAuthBackend` takes the following arguments:
- `identifier`: The identifier to use for the user.


### Basic Usage

```python
from nexios.auth.backends.jwt import JWTAuthBackend

backend = JWTAuthBackend(identifier="id")

app.add_middleware(AuthenticationMiddleware(
    user_model=User,
    backend=backend
))

@app.get("/")
async def index(request: Request, response: Response):
    return {"message": "Hello, world!"}
```

### Issuing a JWT
Nexios provides a simple way to issue a JWT token.

```python
from nexios.auth.backends.jwt import create_jwt

jwt = create_jwt(payload={"id": "123"})
```
- **payload** is the data to include in the token.

**with expires_in**

```python
jwt = create_jwt(payload={"id": "123"}, expires_in=timedelta(minutes=30))
```

::: warning
- Ensure a secret key is set in the config.
- Nexios use pyjwt for JWT authentication, ensure it is installed.
:::

### Other Configuration

```python
from nexios.auth.backends.jwt import JWTAuthBackend
from nexios.config import MakeConfig
app = NexiosApp(config=MakeConfig(
    secret_key="your-secret-key",
    jwt_algorithms=["HS256"],
    
))
backend = JWTAuthBackend(identifier="id")

app.add_middleware(AuthenticationMiddleware(
    user_model=User,
    backend=backend
))
```

## Session Authentication Backend
Nexios provides a built-in `SessionAuthBackend` that you can use to authenticate users with session-based authentication.


### Basic Usage

```python
from nexios.auth.backends.session import SessionAuthBackend
from nexios.config import MakeConfig
from nexios.session import SessionMiddleware
app = NexiosApp(config=MakeConfig(
    secret_key="your-secret-key",
    
))
app.add_middleware(SessionMiddleware())
backend = SessionAuthBackend()

app.add_middleware(AuthenticationMiddleware(
    user_model=User,
    backend=backend
))
```
The `SessionAuthBackend` takes the following arguments:
- `session_key`: The key used to store user data in the session (default: "user")
- `identifier`: The identifier to use for the user.

::: tip Note
- Ensure a session middleware is added to the app.
:::


### Login & Logout

```python
from nexios.auth.backends.session import login, logout

login(request, user)
logout(request)
```
the `login` function takes the following arguments:
- `request`: The HTTP request containing the session
- `user`: The user to login (should be an instance of `BaseUser`)

the `logout` function takes the following arguments:
- `request`: The HTTP request containing the session

## Custom Authentication Backend
You can create a custom authentication backend by implementing the `AuthenticationBackend` interface.  This interface has only one method: `authenticate`. this method should return an `AuthResult` object.

### Basic Example

```python
from nexios.auth.backends.base import AuthenticationBackend
from nexios.auth.model import AuthResult
from nexios.http import Request, Response
class CustomAuthBackend(AuthenticationBackend):
    async def authenticate(self, request: Request, response: Response) -> AuthResult:
        return AuthResult(success=True, identity="123", scope="custom")
```

`AuthResult` takes the following arguments:
- `success`: A boolean indicating whether the authentication was successful.
- `identity`: The unique identifier of the user.
- `scope`: The scope of the authentication (e.g., "jwt", "session").

### What is the scope?
the scope is used to identify the authentication backend that was used to authenticate the user.

### Simple Example

Let's create a simple example of a custom authentication backend. In this example, we will create an authentication backend that checks if the user is in a database.

```python
from nexios.auth.backends.base import AuthenticationBackend
from nexios.auth.base import SimpleUser
from nexios.auth.model import AuthResult
from nexios.http import Request, Response


class DatabaseAuthBackend(AuthenticationBackend):
    async def authenticate(self, request: Request, response: Response) -> AuthResult:
        header = request.headers.get("X-Key")
        if not header:
            return AuthResult(success=False, identity="", scope="database")
        
        return AuthResult(success=True, identity=header, scope="database")


class APIKeyUser(SimpleUser):
    def __init__(self, identity: str, display_name: str):
        self.identity = identity
        self.display_name = display_name

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.display_name

    @property
    def identity(self) -> str:
        return self.identity

    @classmethod
    async def load_user(cls, identity: str) -> APIKeyUser:
        if db.check_api_key(identity):
            return cls(identity=identity, display_name="API Key")
        return None


app.add_middleware(AuthenticationMiddleware(
    user_model=APIKeyUser,
    backend=DatabaseAuthBackend()
))

@app.get("/")
async def index(request: Request, response: Response):
    return {"message": "Hello, world!"}
```
This code defines a custom authentication backend for Nexios, which uses an API key as the identity. The `load_user` method checks if the provided API key exists in the database and returns an `APIKeyUser` instance if it does.

::: tip
- `load_user` is an async method.
:::

## Protected Routes
Nexios provides a simple way to protect routes with authentication.

```python
from nexios.auth.decorators import auth

@app.get("/protected")
@auth()
async def protected_route(request: Request, response: Response):
    return {"message": "This is a protected route"}
```
the `auth` decorator protects the route from unauthenticated requests.


### Using Scope
You can use the `scope` argument to specify the scope of the authentication.

```python
from nexios.auth.decorators import auth

@app.get("/protected")
@auth(scope="jwt")
async def protected_route(request: Request, response: Response):
    return {"message": "This is a protected route"}
```
this will protect the route from unauthenticated requests and only allow requests with a valid JWT token.

### using multiple scopes
You can use the `scopes` argument to specify multiple scopes of the authentication.

```python
from nexios.auth.decorators import auth

@app.get("/protected")
@auth(scopes=["jwt", "session"])
async def protected_route(request: Request, response: Response):
    return {"message": "This is a protected route"}
```
this will protect the route from unauthenticated requests and only allow requests with a valid JWT token or session.




## Permissions (Role Based)
nexios provides a `has_permission` decorator to protect routes with permissions.

```python
from nexios.auth.decorators import has_permission

@app.get("/protected")
@has_permission("admin")
async def protected_route(request: Request, response: Response):
    return {"message": "This is a protected route"}
```

but the user should have the permission to access the route. you can override the `has_permission` method in the user model to check for permissions.

```python
class User(SimpleUser):
    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions
```

### Using multiple permissions
You can use the `permissions` argument to specify multiple permissions of the authentication.

```python
from nexios.auth.decorators import has_permission

@app.get("/protected")
@has_permission(permissions=["admin", "user"])
async def protected_route(request: Request, response: Response):
    return {"message": "This is a protected route"}
```
