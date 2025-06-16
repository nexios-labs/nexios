from nexios import NexiosApp
from nexios.auth.base import AuthenticationBackend, UnauthenticatedUser
from nexios.auth.middleware import AuthenticationMiddleware


class CustomUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @property
    def is_authenticated(self):
        return True

    def get_display_name(self):
        return self.username


class CustomAuthBackend(AuthenticationBackend):
    async def authenticate(self, request, response):
        custom_token = request.headers.get("X-Custom-Token")

        if not custom_token:
            return UnauthenticatedUser(), "no-auth"

        # Add logic to validate token here
        valid_token = True  # Simplified for example

        if valid_token:
            user = CustomUser(id=123, username="example_user")
            return user, "custom-auth"

        return UnauthenticatedUser(), "no-auth"


app = NexiosApp()
custom_backend = CustomAuthBackend()
app.add_middleware(AuthenticationMiddleware(backend=custom_backend))


@app.get("/secure")
async def secure_endpoint(req, res):
    if not req.user.is_authenticated:
        return res.redirect("/login")
    return res.json({"message": "Welcome to the secure endpoint!"})
