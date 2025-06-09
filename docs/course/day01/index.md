# Day 1: Introduction to Nexios

## What You'll Learn
- What Nexios is and its core features
- How to install Nexios and set up your environment
- Creating your first Nexios application
- Understanding the basic project structure

## Core Concepts

### What is Nexios?

Nexios is a modern, high-performance Python web framework designed for building async APIs and web applications. It combines the best of modern Python features with an intuitive API design.

#### Key Features
- Async-first architecture for high performance
- Type-safe development with full type hints
- Intuitive and expressive routing
- Flexible middleware system
- Rich plugin ecosystem
- Modern Python (3.9+) features

## Setting Up Your Environment

### Prerequisites
Make sure you have:
- Python 3.9 or higher
- pip (Python package manager)
- A code editor (VS Code recommended)

### Installation Steps

1. Create a project directory:
```bash
mkdir my-nexios-app
cd my-nexios-app
```

2. Set up a virtual environment:
::: code-group
```bash [Linux/Mac]
python -m venv venv
source venv/bin/activate
```

```bash [Windows]
python -m venv venv
venv\Scripts\activate
```
:::

3. Install Nexios:
```bash
pip install nexios
```

::: tip 💡 Best Practice
Always use a virtual environment to keep your project dependencies isolated!
:::

## Your First Nexios App

### Project Structure
```
my-nexios-app/
├── venv/
└── app.py
```

### Basic Application

Create `app.py`:

```python
from nexios import NexiosApp
from nexios.http import Request, Response

# Create the application
app = NexiosApp()

# Define a route
@app.get("/")
async def hello(request: Request, response: Response):
    return response.json({
        "message": "Hello, World!",
        "framework": "Nexios"
    })

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)
```

::: details 🔍 Code Breakdown
1. **Imports**: 
   - `NexiosApp`: The core application class
   - `Request`: Handles incoming request data
   - `Response`: Manages response formatting

2. **App Creation**: 
   - `app = NexiosApp()` initializes your application

3. **Route Definition**: 
   - `@app.get("/")` defines a GET route
   - The handler function is async for better performance

4. **Running the App**: 
   - Uses `uvicorn` as the ASGI server
   - Development mode with auto-reload enabled
:::

## Working with Responses

Nexios supports multiple response types:

::: code-group
```python [JSON Response]
@app.get("/api/data")
async def json_handler(request, response):
    return response.json({
        "status": "success",
        "data": {"message": "Hello, World!"}
    })
```

```python [Text Response]
@app.get("/text")
async def text_handler(request, response):
    return response.text("Hello, World!")
```

```python [HTML Response]
@app.get("/html")
async def html_handler(request, response):
    return response.html("<h1>Hello, World!</h1>")
```
:::

## Practice Exercise

Create a simple API with multiple endpoints:

```python
@app.get("/about")
async def about(request, response):
    return response.json({
        "app_name": "My First Nexios App",
        "version": "1.0.0",
        "author": "Your Name"
    })

@app.get("/status")
async def status(request, response):
    return response.json({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })
```

##  Homework
1. Create a new Nexios application
2. Add at least 3 different endpoints
3. Use different response types (JSON, text, HTML)
4. Add basic error handling
5. Test your endpoints using a tool like curl or Postman

## Additional Resources
- [Official Nexios Documentation](https://nexios.dev)
- [Python Async/Await Guide](https://docs.python.org/3/library/asyncio.html)
- [Modern Python Features](https://docs.python.org/3/whatsnew/3.7.html)

## Next Steps
Tomorrow in [Day 2: Routing in Nexios](../day02/index.md), we'll explore:
- Route parameters and patterns
- HTTP methods
- Query parameters
- Path parameters
- Request body handling
