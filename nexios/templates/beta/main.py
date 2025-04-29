from nexios import get_application
from routes.index import index
from nexios.routing import Routes
from config import app_config
# Create the application
app = get_application(title="{{project_name_title}}", config=app_config)


app.add_route(
    Routes("/", index,summary="Homepage route", description="Homepage route"),
)