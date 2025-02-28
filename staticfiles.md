

# **Handling Static Files in Nexios**

Nexios provides a simple way to serve static files, such as images, JavaScript, CSS, and other assets, using the `StaticFilesHandler`. This handler maps a URL path to a directory on the filesystem and ensures that only safe files are served.

## **Setting Up Static File Handling**
To serve static files in a Nexios application, you need to initialize and mount the `StaticFilesHandler` with a specific directory and URL prefix.

### **Usage Example**
```python
from nexios.routing import Routes
from pathlib import Path
import os

from static_handler import StaticFilesHandler

# Define the directory for static files
static_directory = Path("static")

# Create an instance of StaticFilesHandler
static_handler = StaticFilesHandler(directory=static_directory, url_prefix="/static/")

# Add route for serving static files
app.add_route(Routes("/static/{path:path}", static_handler))
```

---

## **Understanding the `StaticFilesHandler`**
The `StaticFilesHandler` is responsible for serving files from a specified directory while ensuring security and accessibility.

### **Constructor**
```python
StaticFilesHandler(directory: Union[str, Path], url_prefix: str = "/static/")
```
- **`directory`** (str | Path) – The directory containing static files.
- **`url_prefix`** (str) – The URL prefix under which static files are served. Defaults to `/static/`.

### **Directory Validation**
- If the specified directory does not exist, it will be created automatically.
- If the given path is not a directory, an error is raised.

---

## **Security Measures**
To prevent unauthorized access to sensitive files, `StaticFilesHandler` performs security checks:
1. **Path Validation**  
   - Ensures the requested file is within the specified directory.
   - Prevents directory traversal attacks (e.g., `../../etc/passwd`).
   
2. **Safe Path Resolution**
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

---

## **Request Handling**
When a request is made to access a static file:
- **File Existence Check**  
  If the requested file does not exist or is not a valid file, it returns:
  ```json
  { "error": "Resource not found!" }
  ```
  with a `404 Not Found` status.

- **Serving the File**  
  If the file exists and is valid, it is served with `inline` content disposition:
  ```python
  response.file(file_path, content_disposition_type="inline")
  ```

---

## **Example Request**
Assume we have a file at `static/logo.png` and the `StaticFilesHandler` is set up with `/static/` as the URL prefix.

### **Request:**
```
GET /static/logo.png
```

### **Response:**
The server returns the file `logo.png` if it exists, otherwise a 404 response.

---
