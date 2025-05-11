# Nexios Application Lifecycle

## Introduction

Nexios provides multiple ways to manage application initialization and cleanup:

1. **Decorators**:
   - `on_startup`: Functions to run at application startup.
   - `on_shutdown`: Functions to run at application shutdown.
2. **Lifespan Async Context Manager**: A single async context manager to handle both startup and shutdown logic.

---

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

---

## Application Shutdown

The `@app.on_shutdown()` decorator registers functions to execute when the application shuts down. This is useful for closing database connections, clearing cache, or performing cleanup tasks.

### Example: Closing Database Connections on Shutdown
```python
@app.on_shutdown()
async def shutdown():
    await Tortoise.close_connections()
    print("Application shutting down...")
```

---

## Lifespan Async Context Manager

Nexios also supports using an asynchronous context manager to handle both startup and shutdown events in a single construct. This is achieved by defining a lifespan function and passing it to the application via the `lifespan` argument. This approach encapsulates initialization and cleanup logic in one place.

### Example: Using Lifespan for Database Initialization and Cleanup
```python
from nexios import get_application
from contextlib import asynccontextmanager
from tortoise import Tortoise
from config import DATABASE_CONFIG

@asynccontextmanager
async def app_lifespan(app):
    # Application startup logic
    await Tortoise.init(config=DATABASE_CONFIG)
    await Tortoise.generate_schemas()
    print("Application started successfully!")
    yield
    # Application shutdown logic
    await Tortoise.close_connections()
    print("Application shutting down...")

app = get_application(lifespan=app_lifespan)
```

**Key Notes**:
- The `lifespan` parameter accepts an async context manager that handles both startup (before `yield`) and shutdown (after `yield`).
- Avoid combining this method with `@app.on_startup()`/`@app.on_shutdown()` decorators for the same tasks to prevent redundant execution.

---

By leveraging `on_startup`, `on_shutdown`, or the `lifespan` async context manager, developers can ensure resources are properly initialized and cleaned up, leading to stable and maintainable Nexios applications.