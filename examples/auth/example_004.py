from nexios import NexiosApp
from nexios.auth.decorator import auth
from nexios.http import Request, Response

app = NexiosApp()


@app.get("/dashboard")
@auth(["jwt"])
async def admin_dashboard(req: Request, res: Response):
    if not req.user.is_authenticated:
        return res.redirect("/login")

    return res.html("Welcome to the Admin Dashboard!")


@app.get("/user-profile")
@auth(["session"])
async def user_profile(req: Request, res: Response):
    if not req.user.is_authenticated:
        return res.redirect("/login")

    return res.html("Welcome to your User Profile!")


@app.get("/custom-auth")
@auth(["custom-auth"])
async def custom_auth(req: Request, res: Response):
    if not req.user.is_authenticated:
        return res.redirect("/login")

    return res.html("Welcome to the Custom Auth Page!")
