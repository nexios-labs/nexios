# Nexios Application Lifecycle

## Introduction
Nexios provides two main lifecycle hooks to manage application initialization and cleanup:

1. **Application Startup (`on_startup`)** – Runs when the application starts.
2. **Application Shutdown (`on_shutdown`)** – Runs when the application is shutting down.

## Application Startup
The `@app.on_startup()` decorator registers functions that should execute when the Nexios application starts. This is useful for initializing databases, setting up cache systems, or loading configuration settings.

### Example: Initialize Database on Startup
```python
from nexios import get_application
from tortoise import Tortoise
from config import DATABASE_CONFIG

app = get_application()

async def init_db():
    await Tortoise.init(config=DATABASE_CONFIG)
    await Tortoise.generate_schemas()

@app.on_startup()
async def startup():
    await init_db()
    print("Application started successfully!")
```

## Application Shutdown
The `@app.on_shutdown()` decorator registers functions to execute when the application shuts down. This is useful for closing database connections, clearing cache, or performing cleanup tasks.

### Example: Closing Database Connections on Shutdown
```python
@app.on_shutdown()
async def shutdown():
    await Tortoise.close_connections()
    print("Application shutting down...")
```

By leveraging `on_startup` and `on_shutdown`, developers can ensure that resources are properly initialized and cleaned up, leading to a more stable and maintainable Nexios application.

