from nexios import NexiosApp
from nexios.http import Request, Response

# Create the application
app = NexiosApp(title="{{project_name_title}}")


# Define routes
@app.get("/")
async def index(request: Request, response: Response):
    """Homepage route."""
    return {"message": "Welcome to {{project_name_title}}!", "framework": "Nexios"}
