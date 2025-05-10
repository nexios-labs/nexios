---
icon: file
---

# Static Files

Serving static files is a common requirement for web applications. Nexios provides a robust and flexible system for serving static assets like CSS, JavaScript, images, and other file types with security and performance in mind.

## 🧢 Basic Setup

To serve static files in Nexios, you need to configure a static files handler and mount it to your application:

```python
from nexios import NexiosApp
from nexios.static import StaticFilesHandler
from nexios.routing import Routes
app = NexiosApp()

# Create a static files handler for a single directory
static_handler = StaticFilesHandler(
    directory="static",  # Directory relative to the application root
    url_prefix="/static/"  # URL prefix for accessing static files
)

# Add a route for static files
app.add_route(
    Routes(
        "/static/{path:path}",
        static_handler
    )
)
```

With this setup, a file at `static/css/style.css` would be accessible at `/static/css/style.css`.


### 📁 Single Directory

The simplest configuration uses a single directory for all static files:

```python
static_handler = StaticFilesHandler(
    directory="static",
    url_prefix="/static/"
)
```

## 🗃️ Multiple Directories

For more complex setups, you can serve files from multiple directories:

```python
static_handler = StaticFilesHandler(
    directories=["static", "public/assets", "uploads"],
    url_prefix="/static/"
)
```

When serving from multiple directories, Nexios searches for files in the order the directories are specified.

##  🌐 URL Prefixing

The `url_prefix` parameter defines the URL path under which static files are served:

```python
# Serve files at /assets/ instead of /static/
static_handler = StaticFilesHandler(
    directory="static",
    url_prefix="/assets/"
)
```

