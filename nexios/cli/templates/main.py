from nexios import get_application
from nexios.routing import Routes
from config import nexios_config
from controllers import index

app = get_application(
    config=nexios_config
)


@app.on_startup
async def on_startup():
    print("🚀 Nexios app started successfully!")
    #connect db :optional 

@app.on_shutdown
async def on_shutdown():
    print("🚀 Nexios app stopped successfully!")
    #close db :optional

app.add_route(Routes("/",index))


""" you can add middleware
    app.add_middleware(...)
"""