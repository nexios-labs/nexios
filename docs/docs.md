---
title : Nexios
description : A fast and simple framework for building APIs with Python
icon : 😁
icon_color : #ff7f00
---

# Happy , You made it !

A lightweight, high-performance Python web framework built for speed, simplicity, and flexibility. Inspired by the ease of Express.js and powered by async capabilities.

---

Nexios allows you to create scalable applications quickly without compromising on performance. Whether you're building a microservice or a full-stack solution, Nexios gives you the tools to ship clean, efficient code with ease.

::: warning Important Note
Nexios is designed for modern Python applications. Make sure you're using Python 3.9+ and have a good understanding of async/await patterns for the best experience.
:::

## Simple Example

::: tip What's happening here?
This example demonstrates the core concepts of Nexios: routing, async handlers, and type-safe responses. The framework automatically handles request parsing, response serialization, and error handling.
:::

```python {3}
from nexios import Nexios

app = Nexios()

@app.get("/")
async def home(request: Request, response: Response):
    """Simple endpoint to verify the app is running"""
    return {"message": "Hello, World!"}
```

That's it! You can create API endpoints with just a few lines of code. 🚀

::: warning Performance Consideration
While the example is simple, Nexios is optimized for production use. The framework includes connection pooling, efficient routing, and proper error handling out of the box.
:::

## Where To Start 😕

Getting started with Nexios is quick and simple. Whether you're building your first web app or integrating Nexios into an existing project, you'll find it easy to hit the ground running. Here's how you can get started:

---

### Installation Guide ⬇️

First things first, you need to install Nexios. It's as easy as running the following command:

::: tip Best Practice
Always install dependencies in a virtual environment for project isolation. This prevents conflicts between project dependencies and system packages.
:::

```bash
pip install nexios
```

::: warning Python Version
Nexios requires Python 3.9 or higher for its async features and type hints. Using an older version will result in compatibility issues.
:::

::: tip Version Management
Consider using a tool like `pyenv` or `poetry` to manage Python versions and dependencies. This ensures consistent development environments across your team.
:::

This will install the latest version of Nexios and all its dependencies. You're now ready to start building! For more clarity on the installation process, visit our detailed [installation guide](/docs/getting-started/installation-guide/).

---

### Create Your First Application 🚀

Now that you have Nexios installed, it's time to create your first application. Here's how you can do that:

```bash
nexios new myproject
cd myproject
```

::: tip Project Structure
The `nexios new` command creates a well-organized project structure with:
- Configuration files
- Example routes
- Database models
- Static file handling
- Testing setup
:::

This will create a new directory called `myproject` and install the necessary dependencies. You can then start building your application using the command `nexios run` in your terminal.

### Run Your Application

```bash
nexios run
```

::: tip Development Mode
Use `nexios run --reload` for automatic reloading during development. This feature watches for file changes and automatically restarts the server.
:::

::: warning Production Deployment
Never use the development server in production. Always use a production-grade ASGI server like Uvicorn or Hypercorn with proper configuration.
:::

To run your application, you can use the command `nexios run` in your terminal. This will start the development server and make your application available at http://localhost:4000.

That's it! You're all set to start building your web app with Nexios. Have fun!

## Features

### Fast and Simple Framework 🚀
Built on ASGI with native async/await support, Nexios delivers high performance while maintaining code simplicity.

::: tip Performance
Nexios uses connection pooling and efficient routing for optimal performance:
```python
from nexios.db import Database, ConnectionPool

pool = ConnectionPool(min_size=5, max_size=20)
db = Database(pool)
```

::: warning Resource Management
Always properly configure connection pools based on your application's needs. Too many connections can exhaust system resources, while too few can cause performance bottlenecks.
:::

### Auto OpenAPI Documentation 📃
Automatic API documentation generation with support for OpenAPI/Swagger:

::: tip Documentation Best Practices
- Use descriptive docstrings for all endpoints
- Include example requests and responses
- Document all possible error cases
- Keep schemas up to date with your models
:::

::: code-group
```python [Basic Usage]
@app.get("/items/{item_id}")
async def get_item(request, response, item_id: int):
    """Get an item by ID"""
    return response.json({"id": item_id})
```

```python [With Schema]
from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    price: float

@app.post("/items")
async def create_item(request, response):
    """Create a new item"""
    item = Item(**await request.json())
    return response.json(item)
```
:::

### Authentication 🔒
Built-in authentication with support for multiple backends:

::: warning Security
Always use secure password hashing and token validation in production. Never store plain-text passwords or use weak hashing algorithms.
:::

::: tip Security Best Practices
- Use environment variables for sensitive data
- Implement rate limiting
- Set secure cookie options
- Use HTTPS in production
- Regularly rotate secrets
:::

```python
from nexios.auth import JWTAuth

auth = JWTAuth(secret_key="your-secret")
app.add_middleware(auth.middleware)
```

### CORS Support 🚧
Configurable CORS middleware with safe defaults:

::: warning CORS Security
Be specific with CORS settings. Using `allow_origins=["*"]` in production can expose your API to security risks.
:::

```python
from nexios.middleware import CORSMiddleware

app.add_middleware(CORSMiddleware, 
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)
```

### Async Support 💞
Native async/await support throughout the framework:

::: tip Async Best Practices
- Use connection pooling for databases
- Implement proper error handling
- Don't block the event loop
- Use async context managers for resource cleanup
- Handle concurrent requests properly
:::

::: warning Async Pitfalls
- Avoid CPU-bound operations in async handlers
- Be careful with shared state in async code
- Use proper locking mechanisms when needed
- Monitor memory usage in long-running async operations
:::

### ASGI Compatibility 🧑‍💻
Works with any ASGI server (Uvicorn, Hypercorn, etc.):

::: tip Server Configuration
Configure your ASGI server based on your needs:
- Worker count
- Keep-alive settings
- Timeout values
- Logging configuration
:::

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Built-in CLI Tools 🛠️
Comprehensive CLI for project management:

::: tip CLI Usage
The CLI tools help with:
- Project scaffolding
- Development server
- Database migrations
- Testing
- Code generation
:::

::: code-group
```bash [Create Project]
nexios new myproject
```

```bash [Run Server]
nexios run --reload
```

```bash [Create Component]
nexios generate route users
```
:::

## Who is Nexios For?

### Beginners 🌱
If you're new to web development:
- Simple, intuitive API design
- Comprehensive documentation
- Built-in development tools
- Clear error messages
- Step-by-step tutorials
- Example projects

::: tip Learning Path
Start with the basic examples and gradually explore more advanced features as you become comfortable with the framework.
:::

### Professionals 💼
For experienced developers:
- High performance async capabilities
- Advanced features like dependency injection
- Extensive middleware system
- WebSocket support
- Custom extensions
- Production tooling

::: tip Advanced Usage
Leverage Nexios's advanced features for:
- Microservices architecture
- Real-time applications
- High-throughput APIs
- Complex authentication flows
:::

### Enterprise 🏢
For large-scale applications:
- Scalable architecture
- Security features built-in
- Monitoring and metrics
- Production-ready tools
- Enterprise support
- Compliance features

::: warning Enterprise Considerations
When using Nexios in enterprise environments:
- Implement proper logging and monitoring
- Set up CI/CD pipelines
- Configure security policies
- Plan for scalability
- Document deployment procedures
:::

## Why Use Nexios?

### Simple 📝
::: tip Simplicity
Nexios follows Python's "explicit is better than implicit" principle while reducing boilerplate code. The framework is designed to be intuitive and easy to understand.
:::

### Fast ⚡
::: details Performance Features
- ASGI-based async runtime
- Efficient routing system
- Connection pooling
- Resource management
- Caching support
- Optimized serialization
- Efficient middleware chain
:::

::: warning Performance Tuning
Monitor these aspects for optimal performance:
- Database query patterns
- Memory usage
- CPU utilization
- Network I/O
- Cache hit rates
:::

### Flexible 🔧
::: tip Extensibility
Every part of Nexios can be customized:
- Custom middleware
- Authentication backends
- Database integrations
- Template engines
- Response serializers
- Error handlers
- Logging systems
:::

::: warning Customization
When extending Nexios:
- Follow the framework's patterns
- Maintain backward compatibility
- Document your extensions
- Write tests for custom code
- Consider performance impact
:::

