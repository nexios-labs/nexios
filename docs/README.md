---
icon: home
cover: .gitbook/assets/icon.svg
coverY: 0
---

<div align="center">
<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Ribeye&size=50&pause=1000&color=00ff00&center=true&width=900&height=100&lines=Nexios+Framework;Developed+By+Dunamis" alt="Typing SVG" /></a>

<p align="center">
  <img alt="Nexios" height="350" src="https://raw.githubusercontent.com/nexios-labs/Nexios/90122b22fdd3a57fc1146f472087d483324df0e5/docs/_media/icon.svg"> 
</p>

<h1 align="center">Nexios 2.3.1</h1>

<p align="center">A fast, lightweight and flexible Python web framework inspired by Express.js</p>

<p align="center">
<a href="https://chat.whatsapp.com/KZBM6HMmDZ39yzr7ApvBrC" target="_blank">
  <img src="https://img.shields.io/badge/Join%20WhatsApp%20Group-00C200?style=for-the-badge&logo=whatsapp&logoColor=white" alt="WhatsApp Group Chat" />
</a>
</p>

<p align="center">
<a href="https://github.com/nexios-labs/Nexios?tab=followers"><img title="Followers" src="https://img.shields.io/github/followers/nexios-labs?label=Followers&style=social"></a>
<a href="https://github.com/nexios-labs/Nexios/stargazers/"><img title="Stars" src="https://img.shields.io/github/stars/nexios-labs/Nexios?&style=social"></a>
<a href="https://github.com/nexios-labs/Nexios/network/members"><img title="Fork" src="https://img.shields.io/github/forks/nexios-labs/Nexios?style=social"></a>
<a href="https://github.com/nexios-labs/Nexios/watchers"><img title="Watching" src="https://img.shields.io/github/watchers/nexios-labs/Nexios?label=Watching&style=social"></a>
</p>

<p align="center">
<img src="https://img.shields.io/github/license/nexios-labs/Nexios.svg?style=flat-square" alt="License">
<img src="https://img.shields.io/pypi/v/nexios.svg?style=flat-square" alt="PyPI Version">
<img src="https://img.shields.io/pypi/dm/nexios.svg?style=flat-square" alt="PyPI Downloads">
<img src="https://img.shields.io/pypi/pyversions/nexios.svg?style=flat-square" alt="Python Versions">
<img src="https://img.shields.io/github/issues/nexios-labs/Nexios.svg?style=flat-square" alt="Issues">
<img src="https://img.shields.io/github/release/nexios-labs/Nexios.svg?style=flat-square" alt="Release">
</p>

<p align="center">
<img src="https://profile-counter.glitch.me/{nexios-labs}/count.svg" alt="Nexios Labs:: Visitor's Count" />
</p>

</div>



If Express.js and Python had a wild night of coding, the result would be Nexios—a fast, lightweight, no-nonsense framework that lets you build web apps without the headache.

Think of it as Express.js but speaking fluent Python. It doesn't force you into strict rules, doesn't ask for long configurations, and definitely doesn't judge your coding habits. It just works—so you can focus on writing awesome code instead of wrestling with boilerplate.

## Installation Options

<div align="center">

| Method | Command |
|--------|---------|
| **pip** (recommended) | `pip install nexios` |
| **poetry** | `poetry add nexios` |
| **pipenv** | `pipenv install nexios` |
| **conda** | `conda install -c conda-forge nexios` |
| **git** | `pip install git+https://github.com/nexios-labs/nexios.git` |

</div>

## Getting Started with Nexios

### Simple Hello World

Your first Nexios application can be as simple as:

```python
from nexios import get_application

app = get_application()

@app.get("/")
async def hello(request, response):
    return response.json({"message": "Hello, World!"})


```

### Adding Middleware

Enhance your application with middleware:

```python
from nexios import get_application

async def JSONMiddleware(request, response, next):
    request.json = process_json(request.body)
    return await next()

app = get_application()
app.use(JSONMiddleware)

@app.get("/")
async def index(request, response):
    return response.json({"message": "Welcome to Nexios!"})
```

### Creating Routes with Parameters

Define routes with dynamic parameters:

```python
@app.get("/users/{user_id}")
async def get_user(request, response):
    user_id = request.path_params["user_id"]
    return response.json({"user_id": user_id})
```

### Working with Different HTTP Methods

Handle various HTTP methods with ease:

```python
@app.post("/users")
async def create_user(request, response):
    user_data = await request.json
    # Process user data
    return response.json({"created": True, "user": user_data})

@app.put("/users/{user_id}")
async def update_user(request, response):
    user_id = request.path_params["user_id"]
    updates = await request.json
    # Update user with ID
    return response.json({"updated": True, "id": user_id})

@app.delete("/users/{user_id}")
async def delete_user(request, response):
    user_id = request.path_params["user_id"]
    # Delete user with ID
    return response.json({"deleted": True, "id": user_id})
```

### Using Pydantic for Data Validation

Leverage Pydantic for request validation:

```python
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

@app.post("/users")
async def create_user(request, response):
    data = await request.json
    user = UserCreate(**data)
    return response.json({"created": user.dict()})
```

### Application Lifecycle Events

Handle startup and shutdown events:

```python
@app.on_startup
async def initialize_resources():
    print("Application starting up!")
    # Initialize database connections, etc.

@app.on_shutdown
async def cleanup_resources():
    print("Application shutting down!")
    # Close connections, free resources, etc.
```

## Building a Complete REST API

Here's how to build a task manager API with Nexios:

### 1. Define your models

```python
from typing import List, Optional
from uuid import uuid4, UUID
from pydantic import BaseModel

# Pydantic models
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: UUID
    completed: bool = False

    class Config:
        orm_mode = True
```

### 2. Set up routes with a router

```python
from nexios import get_application
from nexios.http import Request, Response
from nexios.routing import Router
from nexios.exceptions import HTTPException

# Create the app
app = get_application()

# Create a router with a prefix
api_router = Router(prefix="/api")

# In-memory "database"
tasks_db: List[Task] = []
```

### 3. Initialize sample data

```python
@app.on_startup
async def initialize_sample_data():
    global tasks_db
    tasks_db = [
        Task(
            id=uuid4(),
            title="Learn Nexios",
            description="Study the Nexios framework documentation",
            completed=False
        ),
        Task(
            id=uuid4(),
            title="Build API",
            description="Create a task manager API with Nexios",
            completed=True
        )
    ]
    print("Sample data initialized")
```

### 4. Create your CRUD endpoints

```python
@api_router.get("/tasks", responses=List[Task], tags=["tasks"])
async def list_tasks(request: Request, response: Response):
    """List all tasks"""
    return response.json(tasks_db)

@api_router.post("/tasks", responses=Task, tags=["tasks"], request_model=TaskCreate)
async def create_task(request: Request, response: Response):
    """Create a new task"""
    request_body = await request.json
    task_data = TaskCreate(**request_body)
    new_task = Task(
        id=uuid4(),
        title=task_data.title,
        description=task_data.description,
        completed=False
    )
    tasks_db.append(new_task)
    return response.json(new_task)

@api_router.get("/tasks/{task_id}", responses=Task, tags=["tasks"])
async def get_task(request: Request, response: Response):
    """Get a specific task by ID"""
    task_id = UUID(request.path_params["task_id"])
    for task in tasks_db:
        if task.id == task_id:
            return response.json(task)
    raise HTTPException(status_code=404, detail="Task not found")

@api_router.put("/tasks/{task_id}", responses=Task, tags=["tasks"])
async def update_task(request: Request, response: Response):
    """Update a task"""
    task_id = UUID(request.path_params["task_id"])
    request_body = await request.json
    task_update = TaskBase(**request_body)

    for idx, task in enumerate(tasks_db):
        if task.id == task_id:
            updated_task = Task(
                id=task_id,
                title=task_update.title,
                description=task_update.description,
                completed=task.completed
            )
            tasks_db[idx] = updated_task
            return response.json(updated_task)
    raise HTTPException(status_code=404, detail="Task not found")

@api_router.delete("/tasks/{task_id}", tags=["tasks"])
async def delete_task(request: Request, response: Response):
    """Delete a task"""
    global tasks_db
    task_id = UUID(request.path_params["task_id"])
    for idx, task in enumerate(tasks_db):
        if task.id == task_id:
            deleted_task = tasks_db.pop(idx)
            return response.json({"message": f"Task {deleted_task.title} deleted"})
    raise HTTPException(status_code=404, detail="Task not found")
```

### 5. Mount router and run the app

```python
# Mount the API router
app.mount_router(api_router)

# Add a simple root route
@app.get("/")
async def root(request: Request, response: Response):
    return response.json({"message": "Task Manager API is running"})

if __name__ == "__main__":
    # Nexios uses Granian by default
    import granian
    granian.run(app, host="0.0.0.0", port=4000, interface="asgi", access_log=True)
    
    # Or simply use the Nexios CLI:
    # nexios run
```

##  Powered by Granian: Rust-Powered ASGI Server

<div align="center">
<p>
<img src="https://img.shields.io/badge/Powered%20by-Rust-orange?style=for-the-badge&logo=rust" alt="Powered by Rust">
</p>
</div>

Nexios leverages Granian, a high-performance Rust-based ASGI server, providing significant performance advantages:

- **Rust-Powered Core**: The underlying server is written in Rust, offering near-native performance
- **Async by Default**: Built for high-concurrency workloads using Python's async capabilities
- **Optimized Resource Usage**: Lower memory footprint and CPU utilization compared to pure Python servers
- **HTTP/2 Support**: Native support for modern HTTP protocols
- **WebSocket Optimization**: Efficient WebSocket handling for real-time applications

## Feature Checklist

<div align="center">
<table>
<tr>
<td width="50%">

### Core Features
- [x] **Routing with Express-like Syntax**
- [x] **Automatic OpenAPI Documentation**
- [x] **Session Management**
- [x] **File Router System**
- [x] **Authentication (JWT + Custom)**
- [x] **Event System (Signal-based)**
- [x] **Middleware Pipeline**
- [x] **Pydantic Integration**

</td>
<td width="50%">

### Advanced Features
- [x] **Built-in CORS Support**
- [x] **WebSocket Support**
- [x] **Custom Error Handling**
- [x] **Smart Pagination**
- [x] **HTTP/2 Support**
- [x] **High-Performance Async**
- [x] **Rust-Powered Granian Server**
- [x] **JWT Authentication**

</td>
</tr>
</table>
</div>

### Coming Soon 🔜

- [ ] **Inbuilt Database ORM Integration**
- [ ] **Asynchronous Task Queue**
- [ ] **Rate Limiting**
- [ ] **API Throttling**

## 🛠️ CLI Tools

Nexios includes a powerful CLI tool to help you bootstrap projects and run development servers:

### Creating a New Project

```bash
nexios new my_project
```

Options:
* `--output-dir, -o`: Directory where the project should be created (default: current directory)
* `--title`: Display title for the project (defaults to project name)

### Running the Development Server

```bash
nexios run
```

Options:
* `--app, -a`: Application import path (default: main:app)
* `--host`: Host to bind the server to (default: 127.0.0.1)
* `--port, -p`: Port to bind the server to (default: 4000)
* `--reload/--no-reload`: Enable/disable auto-reload (default: enabled)
* `--log-level`: Log level for the server (default: info)
* `--workers`: Number of worker processes (default: 1)

## 💡 Pro Tips

<div class="tip">
<p><strong>Security Tip</strong>: Avoid hardcoding secrets in Nexios; use environment variables for better security!</p>

```python
from os import getenv

SECRET_KEY = getenv("APP_SECRET_KEY")
DATABASE_URL = getenv("DATABASE_URL")
```
</div>

## 📊 Performance Comparison

<div align="center">

| Framework | Requests/sec | Latency (ms) | Memory Usage |
|-----------|--------------|--------------|--------------|
| FastAPI+Uvicorn | ~45,000 | ~2.0 | Medium |
| **Nexios+Granian** | ~42,000 | ~2.4 | Low |
| Flask+Gunicorn | ~20,000 | ~5.0 | Medium |
| Django+Gunicorn | ~15,000 | ~6.5 | High |

</div>

*Note: Benchmarks performed on standard hardware. Your results may vary based on configuration and use case.*

## 📸 OpenAPI Documentation

<p align="center">
  <img src="../docs/_media/openapi.jpg" alt="OpenAPI Screenshot"/>
</p>

After running your Nexios application, visit `http://localhost:4000/docs` to access the automatically generated Swagger documentation.

## 🗣️ What Developers Say

<div class="testimonial">
<blockquote>
"Adopting Nexios at our startup has been a practical and effective choice. In a fast-moving development environment, we needed something lightweight and efficient — Nexios met that need.

Its clean architecture and compatibility with different ORMs helped our team work more efficiently and keep things maintainable. One of its strengths is how straightforward it is — minimal overhead, just the tools we need to build and scale our backend services."

— Joseph Mmadubuike, Chief Technology Officer at buzzbuntu.com
</blockquote>
</div>

## 🤝 Join Our Community

Get involved with Nexios development and connect with other developers:

<div align="center">
<p>
<a href="https://chat.whatsapp.com/KZBM6HMmDZ39yzr7ApvBrC">
  <img src="https://img.shields.io/badge/Join%20WhatsApp-Community-00C200?style=for-the-badge&logo=whatsapp&logoColor=white" alt="WhatsApp Community" />
</a>
</p>

<p>
<a href="https://nexios-labs.gitbook.io/nexios">
  <img src="https://img.shields.io/badge/Read-Documentation-blue?style=for-the-badge&logo=gitbook&logoColor=white" alt="Documentation" />
</a>
</p>
</div>

- 📚 [Read the Docs](https://nexios-labs.gitbook.io/nexios)
- 💬 [Join WhatsApp Group](https://chat.whatsapp.com/KZBM6HMmDZ39yzr7ApvBrC)
- 🐱 [GitHub Repository](https://github.com/nexios-labs/Nexios)
- 🐛 [Report Issues](https://github.com/nexios-labs/Nexios/issues)
- 🤝 [Contribute](https://github.com/nexios-labs/Nexios/blob/main/CONTRIBUTING.md)

## ☕ Support Nexios

Nexios is a passion project built to make backend development in Python faster, cleaner, and more developer-friendly. It's fully open-source and maintained with love, late nights, and lots of coffee.

If Nexios has helped you build something awesome, consider supporting its continued development. Your donation helps cover:

- 📚 Documentation hosting and tools
- 🚀 New feature development
- 🐛 Bug fixes and maintenance
- 🎓 Tutorial and example creation
- 🌐 Community support resources

<div align="center">
<p>
<a href="https://www.buymeacoffee.com/techwithdul">
  <img src="https://img.shields.io/badge/Buy%20me%20a%20coffee-Support%20Development-yellow?style=for-the-badge&logo=buy-me-a-coffee&logoColor=white" alt="Buy Me A Coffee" />
</a>
</p>
</div>

Every contribution, no matter how small, helps keep Nexios growing and improving. Thank you for your support! 🙏

## 📚 Full Documentation

For complete documentation, visit our [GitBook](https://nexios-labs.gitbook.io/nexios).

<div align="center">
<h2>Star the repo if you like it! ⭐</h2>
</div>

