from nexios import get_application
from routes.index.route import index_router
from config import app_config
# Create the application
app = get_application(title="{{project_name_title}}", config=app_config)




app.mount_router(index_router)