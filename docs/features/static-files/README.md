---
icon: file
---

# Static Files

Serving static files is a common requirement for web applications. Nexios provides a robust and flexible system for serving static assets like CSS, JavaScript, images, and other file types with security and performance in mind.

## Basic Setup

To serve static files in Nexios, you need to configure a static files handler and mount it to your application:

```python
from nexios import get_application
from nexios.static import StaticFilesHandler

app = get_application()

# Create a static files handler for a single directory
static_handler = StaticFilesHandler(
    directory="static",  # Directory relative to the application root
    url_prefix="/static/"  # URL prefix for accessing static files
)

# Add a route for static files
@app.get("/static/{path:path}")
async def serve_static(req, res):
    return await static_handler(req, res)
```

With this setup, a file at `static/css/style.css` would be accessible at `/static/css/style.css`.

## Configuration Options

### Single Directory

The simplest configuration uses a single directory for all static files:

```python
static_handler = StaticFilesHandler(
    directory="static",
    url_prefix="/static/"
)
```

### Multiple Directories

For more complex setups, you can serve files from multiple directories:

```python
static_handler = StaticFilesHandler(
    directories=["static", "public/assets", "uploads"],
    url_prefix="/static/"
)
```

When serving from multiple directories, Nexios searches for files in the order the directories are specified.

### URL Prefixing

The `url_prefix` parameter defines the URL path under which static files are served:

```python
# Serve files at /assets/ instead of /static/
static_handler = StaticFilesHandler(
    directory="static",
    url_prefix="/assets/"
)
```

## Directory Handling and Security

### Directory Safety

The StaticFilesHandler includes security measures to prevent directory traversal attacks:

1. **Path Normalization**: Paths are normalized to prevent accessing files outside the specified directories.
2. **Safe Path Checking**: Each request is validated to ensure it resolves to a path within the allowed directories.

### Auto-Creation of Directories

By default, if the specified static directory doesn't exist, Nexios will create it:

```python
# This will create the "static_files" directory if it doesn't exist
static_handler = StaticFilesHandler(directory="static_files")
```

To disable this behavior, you would need to modify the StaticFilesHandler or ensure the directory exists before starting your application.

## File Types and MIME Types

### MIME Type Detection

Nexios automatically detects the appropriate MIME type for files based on their extension using Python's `mimetypes` module:

```python
# This file would be served with Content-Type: text/css
# /static/styles.css 

# This file would be served with Content-Type: image/png
# /static/logo.png
```

### Default MIME Type

If the MIME type cannot be determined, Nexios uses `application/octet-stream` as the default:

```python
# This file would be served with Content-Type: application/octet-stream
# /static/unknown-extension.xyz
```

## Advanced Usage

### Custom Response Headers

You can add custom headers to static file responses by extending the StaticFilesHandler:

```python
from nexios.static import StaticFilesHandler

class CustomStaticFilesHandler(StaticFilesHandler):
    async def __call__(self, request, response):
        res = await super().__call__(request, response)
        
        # Add cache control headers
        if res.status_code == 200:
            res.set_header("Cache-Control", "public, max-age=31536000")
        
        return res

# Use the custom handler
static_handler = CustomStaticFilesHandler(directory="static")
```

### Conditional Responses

Nexios static file handling supports conditional requests with proper ETag and Last-Modified headers:

```python
from nexios.static import StaticFilesHandler
from email.utils import formatdate
import os, hashlib

class ConditionalStaticHandler(StaticFilesHandler):
    async def __call__(self, request, response):
        path = request.path_params.get("path", "")
        
        for directory in self.directories:
            file_path = (directory / path).resolve()
            
            if self._is_safe_path(file_path) and file_path.is_file():
                # Check If-Modified-Since header
                if_modified_since = request.headers.get("if-modified-since")
                stat_result = os.stat(file_path)
                last_modified = formatdate(stat_result.st_mtime, usegmt=True)
                
                if if_modified_since and if_modified_since == last_modified:
                    return response.empty(status_code=304)  # Not Modified
                
                # Calculate ETag
                etag_base = f"{stat_result.st_mtime}-{stat_result.st_size}"
                etag = f'"{hashlib.md5(etag_base.encode()).hexdigest()}"'
                
                # Check If-None-Match header
                if_none_match = request.headers.get("if-none-match")
                if if_none_match and if_none_match == etag:
                    return response.empty(status_code=304)  # Not Modified
                
                # Set headers and return file
                response.set_header("Last-Modified", last_modified)
                response.set_header("ETag", etag)
                return response.file(str(file_path))
        
        return response.json("Resource not found", status_code=404)
```

### Streaming Large Files

For large files, Nexios uses asynchronous file streaming with chunked responses:

```python
# The FileResponse class automatically streams large files in chunks
# This prevents loading the entire file into memory

@app.get("/download/{filename}")
async def download_file(req, res):
    filename = req.path_params.filename
    return res.file(
        f"downloads/{filename}",
        content_disposition_type="attachment"  # Force download
    )
```

### Range Requests

Nexios's file handling supports HTTP range requests for partial content and resumable downloads:

```python
# This is handled automatically by the FileResponse class
# Range requests are important for video streaming and large file downloads
```

## Examples

### Basic Static File Setup

```python
from nexios import get_application
from nexios.static import StaticFilesHandler
from pathlib import Path

app = get_application()

# Get current directory
current_dir = Path(__file__).parent

# Set up static files
static_handler = StaticFilesHandler(
    directory=current_dir / "static",
    url_prefix="/static/"
)

# Route for static files
@app.get("/static/{path:path}")
async def serve_static(req, res):
    return await static_handler(req, res)

# Normal routes
@app.get("/")
async def index(req, res):
    return res.html("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nexios App</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <h1>Welcome to Nexios</h1>
        <img src="/static/images/logo.png" alt="Logo">
        <script src="/static/js/app.js"></script>
    </body>
    </html>
    """)
```

### Multiple Static Directories for Different Purposes

```python
from nexios import get_application
from nexios.static import StaticFilesHandler

app = get_application()

# Public assets (CSS, JS, images)
public_handler = StaticFilesHandler(
    directory="public",
    url_prefix="/assets/"
)

# User uploads (avatar images, files)
uploads_handler = StaticFilesHandler(
    directory="uploads",
    url_prefix="/uploads/"
)

# Routes for static files
@app.get("/assets/{path:path}")
async def serve_public(req, res):
    return await public_handler(req, res)

@app.get("/uploads/{path:path}")
async def serve_uploads(req, res):
    return await uploads_handler(req, res)
```

### Media and Download System

```python
from nexios import get_application
from nexios.static import StaticFilesHandler

app = get_application()

# Media files handler
media_handler = StaticFilesHandler(
    directory="media",
    url_prefix="/media/"
)

# Download files handler
downloads_handler = StaticFilesHandler(
    directory="downloads",
    url_prefix="/downloads/"
)

@app.get("/media/{path:path}")
async def serve_media(req, res):
    # Media files (stream inline)
    return await media_handler(req, res)

@app.get("/downloads/{path:path}")
async def serve_downloads(req, res):
    # Download the file instead of displaying inline
    path = req.path_params.get("path", "")
    
    # Find file in downloads directory
    for directory in downloads_handler.directories:
        file_path = (directory / path).resolve()
        
        if downloads_handler._is_safe_path(file_path) and file_path.is_file():
            # Force download instead of inline display
            return res.download(str(file_path))
    
    return res.json("Download not found", status_code=404)
```

## Best Practices

1. **Separate Static Files from Application Code**: Keep your static files in a dedicated directory separate from your application code.

2. **Use a CDN for Production**: For production environments, consider serving static files from a CDN for better performance.

3. **Enable Caching**: Set appropriate cache headers for static files to improve performance.

4. **Compress Static Files**: Enable GZIP compression for text-based static files (CSS, JS, HTML) to reduce transfer size.

5. **Use Versioning**: Add version numbers or hashes to static file URLs to ensure clients always get the latest version after updates.

6. **Security Considerations**: 
   - Never allow serving files from sensitive directories
   - Validate and sanitize file paths
   - Set appropriate Content-Security-Policy headers

## Conclusion

Nexios provides a flexible and secure system for serving static files. The StaticFilesHandler makes it easy to configure how and where files are served, while built-in security measures help prevent common vulnerabilities.

---
icon: images
---

# Static Files

Nexios provides a simple way to serve static files, such as images, JavaScript, CSS, and other assets, using the `StaticFilesHandler`. This handler maps a URL path to a directory on the filesystem and ensures that only safe files are served.

## **Setting Up Static File Handling**

To serve static files in a Nexios application, you need to initialize and mount the `StaticFilesHandler` with a specific directory and URL prefix.

### **Usage Example**

```python
from nexios.routing import Routes
from pathlib import Path
import os

from nexios.static import StaticFilesHandler

# Define the directory for static files
static_directory = Path("static")

# Create an instance of StaticFilesHandler
static_handler = StaticFilesHandler(directory=static_directory, url_prefix="/static/")

# Add route for serving static files
app.add_route(Routes("/static/{path:path}", static_handler))
```

***

## **Understanding the `StaticFilesHandler`**

The `StaticFilesHandler` is responsible for serving files from a specified directory while ensuring security and accessibility.

### **Constructor**

```python
StaticFilesHandler(directory: Union[str, Path], url_prefix: str = "/static/")
```

* **`directory`** (str | Path) – The directory containing static files.
* **`url_prefix`** (str) – The URL prefix under which static files are served. Defaults to `/static/`.

### **Directory Validation**

* If the specified directory does not exist, it will be created automatically.
* If the given path is not a directory, an error is raised.

***

## **Security Measures**

To prevent unauthorized access to sensitive files, `StaticFilesHandler` performs security checks:

1. **Path Validation**
   * Ensures the requested file is within the specified directory.
   * Prevents directory traversal attacks (e.g., `../../etc/passwd`).
2.  **Safe Path Resolution**

    ```python
    def _is_safe_path(self, path: Path) -> bool:
        """Check if the path is safe to serve"""
        try:
            full_path = path.resolve()
            return str(full_path).startswith(str(self.directory))
        except (ValueError, RuntimeError):
            return False
    ```

    This ensures that only files within the allowed directory are served.

***

## **Request Handling**

When a request is made to access a static file:

*   **File Existence Check**\
    If the requested file does not exist or is not a valid file, it returns:

    ```json
    { "error": "Resource not found!" }
    ```

    with a `404 Not Found` status.
*   **Serving the File**\
    If the file exists and is valid, it is served with `inline` content disposition:

    ```python
    response.file(file_path, content_disposition_type="inline")
    ```

***

## **Example Request**

Assume we have a file at `static/logo.png` and the `StaticFilesHandler` is set up with `/static/` as the URL prefix.

### **Request:**

```
GET /static/logo.png
```

### **Response:**

The server returns the file `logo.png` if it exists, otherwise a 404 response.

***
