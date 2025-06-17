from nexios import get_application
from nexios.routing import Routes

from config import app_config
from routes.index import index

# Create the application
app = get_application(title="{{project_name_title}}", config=app_config)


@app.on_startup
async def startup():
    """Function that runs on application startup."""
    print("{{project_name_title}} starting up...")


@app.on_shutdown
async def shutdown():
    """Function that runs on application shutdown."""
    print("{{project_name_title}} shutting down...")


app.add_route(
    Routes("/", index, summary="Homepage route", description="Homepage route"),
)
