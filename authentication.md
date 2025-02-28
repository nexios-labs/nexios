#### Authentication

The authentication system in Nexios is built with modern API security practices in mind. It supports a variety of authentication methods, including JSON Web Tokens (JWT), API keys, and session-based authentication. The system is designed to be fully asynchronous, ensuring that authentication processes do not block your application's performance.

## Basic Configuration

To enable authentication in your API, you need to configure the authentication middleware. This middleware handles the validation of authentication tokens, session management, and user retrieval.

Here’s an example of how to set up the authentication middleware with JWT:

> Note:  some authentication backend configuration might require `secret_key` , ensure to add secret key to the application configuration


```py


from nexios import get_application
from  nexios.auth.backends import  JWTAuthBackend
from nexios.auth.middleware import AuthenticationMiddleware

app = get_application()

async def validation_funtion(**kwaargs):
    #kwargs is returned from the jwt payload
    #db checks
    #return UserModel
app.add_middleware(
    AuthenticationMiddleware(
        backend = JWTAuthBackend(authenticate_func = validation_funtion)
    )
)

```


Nexios keeps authentication simple and fast with its fully async system. The code sets up JWT authentication using `AuthenticationMiddleware`, which checks every request for a valid token. It works with `JWTAuthBackend` to decode the JWT and pass its data to a custom validation function. This function runs extra checks, like verifying the user in the database, before allowing access.  

Adding authentication is just one line with `app.add_middleware`, keeping things clean and easy. The validation function is async, so it handles database lookups without slowing things down. Since JWT relies on secure signatures, setting a `SECRET_KEY` in your config is a must. This setup ensures smooth, secure authentication without the hassle.


## Protected Routes

In Nexios, a protected route ensures only authenticated users can access certain endpoints. The `AuthenticationMiddleware` processes each request by verifying the token and calling the `authenticate_func`. If authentication is successful, `request.user` is set to the returned user object, and `request.scope["auth"]` is set to the authentication method (e.g., `"jwt"`). If authentication fails, `request.user` defaults to an `UnauthenticatedUser`, preventing unauthorized access while maintaining a consistent request structure.


**Basic example**

```py
from nexios.auth.decorator import auth 

@app.get("/protected-resource")
@auth(['jwt'])
async def protectd_resource_handler(req, res):
    print(request.user) #ouput the return value of the authenticator_func in the authentication backend if user is authenticated


```



### **API Key Authentication in Nexios**  

Like JWT, Nexios provides an `APIKeyAuthBackend` that verifies API keys and ensures that only authorized users can access the system.  

---

### **Setting Up API Key Authentication**  

```python
from nexios import get_application
from nexios.auth.backends import APIKeyAuthBackend
from nexios.auth.middleware import AuthenticationMiddleware

app = get_application()

async def validate_api_key(api_key: str):
    """
    Custom function to validate API key.
    This should check against a database or other storage.
    """
    # Example: Query the database for a user with this API key
    user = await get_user_by_api_key(api_key)
    if user:
        return user
    return None  # Authentication will fail if None is returned

app.add_middleware(
    AuthenticationMiddleware(
        backend=APIKeyAuthBackend(authenticate_func=validate_api_key, header_name="X-API-KEY")
    )
)
```

This setup ensures that every request containing an `X-API-KEY` header is validated before proceeding.  

- **`validate_api_key` function**: This function receives the API key and checks if it belongs to a valid user in the database.  
- **`APIKeyAuthBackend`**: This backend handles extracting and verifying API keys from incoming requests.  
- **Asynchronous validation**: Ensures that database lookups don’t block the application.  

---

### **Protecting Routes with API Key Authentication**  

To restrict access to certain routes, use the `@auth` decorator with the `api_key` authentication method.  

```python
from nexios.auth.decorator import auth 

@app.get("/secure-data")
@auth(["api_key"])
async def secure_data_handler(req, res):
    print(req.user)  # Outputs the authenticated user object
    res.json({"message": "You have access to secure data!"})
```


## Creating a Custom Authentication Backend in Nexios
Nexios allows developers to implement custom authentication backends, providing flexibility to support different authentication mechanisms, such as OAuth, custom tokens, or database-driven authentication.

**Defining a Custom Authentication Backend**

```py

from nexios.auth.backends import BaseAuthBackend

class CustomAuthBackend(BaseAuthBackend):
    """
    Custom authentication backend that validates users 
    based on a custom header value.
    """

    async def authenticate(self, request, response):
        token = request.headers.get("X-CUSTOM-AUTH")
        
        if not token:
            return None  
        
        user = await self.validate_custom_token(token)

        return user  

    async def validate_custom_token(self, token):
        """
        Custom token validation logic (replace with database checks).
        """
        fake_users = {
            "valid-token-123": {"id": 1, "username": "JohnDoe"},
            "valid-token-456": {"id": 2, "username": "JaneDoe"},
        }
        return fake_users.get(token)

```
**Integrating the Custom Backend with Middleware**

Once the backend is created, integrate it with Nexios' authentication middleware.
```py
from nexios import get_application
from nexios.auth.middleware import AuthenticationMiddleware

app = get_application()

app.add_middleware(
    AuthenticationMiddleware(
        backend=CustomAuthBackend()
    )
)


```

## Creating a User Model in Nexios
Since Nexios doesn’t come with its own ORM, it provides base classes that can be integrated with third-party ORMs like Tortoise-ORM, SQLAlchemy, Django ORM, or others.

This guide demonstrates how to create a User Model in Nexios using Tortoise-ORM, which is an asynchronous ORM for Python.


**Defining the User Model**
Nexios provides a BaseUser class that can be extended when defining a user model. This ensures compatibility with authentication mechanisms while allowing customization.

```py
from tortoise import fields, models
from nexios.auth.base import BaseUser

class UserModel(models.Model, BaseUser):
    """
    Custom User model for Nexios authentication with Tortoise-ORM.
    """
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)

    class Meta:
        table = "users"  # Optional: Define table name

    def __str__(self):
        return self.username



```

### Nexios Base Methods Overview  

Nexios provides several base methods that can be overridden when integrating with an ORM like Tortoise.  

#### Overridable Methods:  
- **`authenticate(req, res)`** – Validates user credentials.  
- **`is_authenticated`** – Checks if the user is authenticated.  
- **`display_name`** – Returns the user’s display name.  
- **`identity`** – Provides a unique user identifier.  

These methods allow customization to fit different authentication and user management needs.