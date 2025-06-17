from nexios import NexiosApp

from config import app_config
from routes.index.route import index_router

# Create the application
app = NexiosApp(title="{{project_name_title}}", config=app_config)


app.mount_router(index_router)


@app.on_startup
async def startup():
    """Function that runs on application startup."""
    print("{{project_name_title}} starting up...")


@app.on_shutdown
async def shutdown():
    """Function that runs on application shutdown."""
    print("{{project_name_title}} shutting down...")
