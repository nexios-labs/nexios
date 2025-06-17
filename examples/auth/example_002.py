from nexios import NexiosApp
from nexios.auth.backends.jwt import JWTAuthBackend, create_jwt
from nexios.auth.base import BaseUser
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.http import Request, Response


class User(BaseUser):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    @property
    def identity(self):
        return self.id

    @property
    def is_authenticated(self):
        return True

    @property
    def display_name(self):
        return self.username


app = NexiosApp()


async def get_user_by_id(**payload):
    return User(id=payload["id"], username=payload["sub"], email="")


app.add_middleware(
    AuthenticationMiddleware(backend=JWTAuthBackend(authenticate_func=get_user_by_id))
)


@app.route("/login", methods=["POST"])
async def login(req: Request, res: Response):
    form = await req.form_data
    username = form.get("username")
    password = form.get("password")

    if username == "admin" and password == "password":
        payload = {"sub": username}
        token = create_jwt(payload)
        return {
            "token": token,
        }
    return res.html("Invalid username or password", status_code=401)


@app.route("/logout", methods=["POST"])
async def logout(req: Request, res: Response):

    return res.redirect("/login")


@app.route("/protected")
async def protected(req: Request, res: Response):
    if req.user.is_authenticated:
        return res.html(f"Hello, {req.user.username}!")
    return res.redirect("/login")
