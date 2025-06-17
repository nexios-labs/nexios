from nexios import NexiosApp
from nexios.auth.backends.session import SessionAuthBackend
from nexios.auth.middleware import AuthenticationMiddleware

app = NexiosApp()


class db:

    @classmethod
    async def get_user(cls, user_id):
        return {"id": user_id, "username": "user", "password": "password"}


async def get_user_by_id(user_id: int):
    # Load user by ID
    user = await db.get_user(user_id)
    return user


session_backend = SessionAuthBackend(
    user_key="user_id",  # Session key for user ID
    authenticate_func=get_user_by_id,  # Function to load user by ID
)

app.add_middleware(AuthenticationMiddleware(backend=session_backend))


@app.get("/login")
async def login(req, res):
    return """
    <form action="/login" method="post">
        <label>Username: <input type="text" name="username"></label>
        <label>Password: <input type="password" name="password"></label>
        <input type="submit" value="Login">
    </form>
    """


@app.post("/login")
async def login_post(req, res):
    req.form["username"]
    password = req.form["password"]
    user = await get_user_by_id(1)  # hardcoded user ID for demonstration
    if user and user.check_password(password):
        req.session["user_id"] = user.id
        return res.redirect("/protected")
    return res.html("Invalid username or password", status_code=401)


@app.get("/protected")
async def protected(req, res):
    user = req.user
    if user:
        return res.html(f"Hello, {user.username}!")
    return res.redirect("/login")


@app.get("/logout")
async def logout(req, res):
    req.session.pop("user_id", None)
    return res.redirect("/login")
