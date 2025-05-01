from nexios import get_application
from nexios.routing import Router

auth_router = Router()


@auth_router.post("/login")
async def login(req, res):
    credentials = await req.json
    # Simulate authentication
    if (
        credentials.get("username") == "admin"
        and credentials.get("password") == "secret"
    ):
        return res.json({"token": "dummy_jwt_token"})
    return res.json({"error": "Invalid credentials"}, status_code=401)


app = get_application()
app.mount_router("/auth", auth_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)
