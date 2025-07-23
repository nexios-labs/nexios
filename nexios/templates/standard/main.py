from nexios import NexiosApp

from nexios.templating import render, TemplateEngine
from routes.index.route import index_router


app = NexiosApp()
engine = TemplateEngine()
engine.setup_environment()


app.mount_router(index_router)


@app.on_startup
async def startup():
    """Function that runs on application startup."""
    print("{{project_name_title}} starting up...")


@app.on_shutdown
async def shutdown():
    """Function that runs on application shutdown."""
    print("{{project_name_title}} shutting down...")
