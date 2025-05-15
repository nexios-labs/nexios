from nexios import NexiosApp
from nexios.http import Request, Response

# Create the application
app = NexiosApp(title="{{project_name_title}}")


# Define routes
@app.get("/")
async def index(request: Request, response: Response):
    """Homepage route."""
    return response.json(
        {"message": "Welcome to {{project_name_title}}!", "framework": "Nexios"}
    )


@app.get("/hello/{name}")
async def hello(request: Request, response: Response):
    """Say hello to a user."""
    name = request.path_params.get("name", "World")
    return response.json({"message": f"Hello, {name}!"})


# Application lifecycle hooks
@app.on_startup
async def startup():
    """Function that runs on application startup."""
    print("{{project_name_title}} starting up...")


@app.on_shutdown
async def shutdown():
    """Function that runs on application shutdown."""
    print("{{project_name_title}} shutting down...")


