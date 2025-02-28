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
app.add_middleware(
    AuthenticationMiddleware(
        backend = JWTAuthBackend(authenticate_func = validation_funtion)
    )
)

```


Nexios keeps authentication simple and fast with its fully async system. The code sets up JWT authentication using `AuthenticationMiddleware`, which checks every request for a valid token. It works with `JWTAuthBackend` to decode the JWT and pass its data to a custom validation function. This function runs extra checks, like verifying the user in the database, before allowing access.  

Adding authentication is just one line with `app.add_middleware`, keeping things clean and easy. The validation function is async, so it handles database lookups without slowing things down. Since JWT relies on secure signatures, setting a `SECRET_KEY` in your config is a must. This setup ensures smooth, secure authentication without the hassle.


## Protected Routes

In Nexios, a protected route ensures only authenticated users can access specific endpoints. The `AuthenticationMiddleware` validates the request by running `authenticate_func`. If authentication succeeds, `request.user` is set to whatever `authenticate_func` returns, and `request.scope["auth"]` is set accordingly (e.g., `"jwt"`). If authentication fails, `request.user` is set to an `UnauthenticatedUser`, maintaining consistency while blocking unauthorized access.