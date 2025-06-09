# Day 1: Introduction to Nexios

Welcome to your first day of learning Nexios! Today, we'll cover the fundamentals and create our first Nexios application.

## What is Nexios?

Nexios is a modern, fast, and flexible Python web framework designed for building APIs and web applications. It features:
- Async-first architecture
- Type hints support
- Intuitive routing
- Built-in middleware system
- Extensive plugin ecosystem

## Installation and Setup

1. Create a new project directory:
```bash
mkdir my-nexios-app
cd my-nexios-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install Nexios:
```bash
pip install nexios
```

## Your First Nexios Application

Let's create a simple "Hello, World!" application:

```python
# app.py
from nexios import NexiosApp
from nexios.http import Request, Response

# Create the application
app = NexiosApp()

# Define a route
@app.get("/")
async def index(request: Request, response: Response):
    return response.json({
        "message": "Hello, World!",
        "framework": "Nexios"
    })

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)
```

## Understanding the Code

Let's break down the key components:

1. **Imports**:
   - `NexiosApp`: The main application class
   - `Request`: Handles incoming HTTP requests
   - `Response`: Manages HTTP responses

2. **Application Instance**:
   ```python
   app = NexiosApp()
   ```
   Creates a new Nexios application instance.

3. **Route Decorator**:
   ```python
   @app.get("/")
   ```
   Defines a route handler for GET requests to the root path ("/").

4. **Route Handler**:
   ```python
   async def index(request: Request, response: Response):
   ```
   - Async function that handles the request
   - Takes `request` and `response` parameters
   - Returns a JSON response

5. **Running the App**:
   ```python
   uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)
   ```
   Starts the development server with hot reload enabled.

## Basic Response Types

Nexios supports various response types:

```python
# JSON Response
@app.get("/json")
async def json_handler(request, response):
    return response.json({"message": "Hello, World!"})

# Text Response
@app.get("/text")
async def text_handler(request, response):
    return response.text("Hello, World!")

# HTML Response
@app.get("/html")
async def html_handler(request, response):
    return response.html("<h1>Hello, World!</h1>")
```

## Exercises

1. **Basic Route**:
   Create a route that returns your name and favorite programming language.

2. **Multiple Routes**:
   Add routes for `/about` and `/contact` that return different JSON responses.

3. **Custom Headers**:
   Modify the index route to include a custom header `X-Powered-By: Nexios`.

## Mini-Project: Simple API

Create a simple API with the following endpoints:
1. GET `/api/items` - Returns a list of items
2. GET `/api/items/{item_id}` - Returns a specific item

```python
from nexios import NexiosApp

app = NexiosApp()

# Sample data
items = [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"},
    {"id": 3, "name": "Item 3"}
]

@app.get("/api/items")
async def get_items(request, response):
    return response.json(items)

@app.get("/api/items/{item_id:int}")
async def get_item(request, response):
    item_id = request.path_params.item_id
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        return response.json(item)
    return response.json({"error": "Item not found"}, status_code=404)
```

## Key Concepts Learned

- Setting up a Nexios application
- Creating basic routes
- Handling requests and responses
- Working with JSON data
- Basic path parameters
- HTTP status codes

## Additional Resources

- [Nexios Documentation](https://nexios.dev)
- [API Examples](https://nexios.dev/examples)
- [GitHub Repository](https://github.com/yourusername/nexios)

## Homework

1. Add more routes to the mini-project:
   - GET `/api/items/search?name=query` - Search items by name
   - GET `/api/status` - Return API status and version

2. Experiment with different response types:
   - Try returning HTML
   - Add custom headers
   - Use different status codes

3. Read the documentation on routing and responses

## Next Steps

Tomorrow, we'll dive deeper into routing patterns and request handling in [Day 2: First Application & Routing](../day02/index.md). 