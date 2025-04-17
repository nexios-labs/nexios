## `NEXIOS`

<div align="left">
<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Ribeye&size=50&pause=1000&color=00ff00&center=true&width=900&height=100&lines=Nexios+Framework;Developed+By+Dunamis" alt="Typing SVG" /></a>

<p align="center">
  <a href="">
    <img alt=Support height="350" src="https://raw.githubusercontent.com/nexios-labs/Nexios/90122b22fdd3a57fc1146f472087d483324df0e5/docs/_media/icon.svg"> 
    </p>
    <h1 align="center">Nexios 2.3.1<br></h1>
    
   </a>
</p>
  
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

<p align="center"><img src="https://profile-counter.glitch.me/{nexios-labs}/count.svg" alt="Nexios Labs:: Visitor's Count" /></p>

</br>

<h2 align="center"> Star the repo if u like it🌟
</h2>

Nexios is a lightweight, Python-based web framework designed for speed, flexibility, and simplicity. It supports RESTful APIs, authentication, and integrates easily with any ORM. Built for modern web development, Nexios allows developers to quickly spin up scalable, modular apps with minimal boilerplate—ideal for startups, rapid prototyping, and custom backend solutions. Think Django's speed, Flask's minimalism.

---

## `Tips`

Avoid Hardcoding Secrets in Nexios; Use Environment Variables for Better Security!

---

## `Installation`

To install **Nexios**, you can use several methods depending on your environment and preferred package manager. Below are the instructions for different package managers:

### 1. **From `pip`** (Standard Python Package Manager)

To install Nexios using `pip`, the most common Python package manager, run the following command:

```bash
pip install nexios
```

### 2. **Using `pipenv`** (Python Dependency Management)

If you're managing your project's dependencies with `pipenv`, use the following command:

```bash
pipenv install nexios
```

### 3. **Using `conda`** (For Conda Environments)

If you're working with Conda environments, you can install Nexios from the Conda Forge channel:

```bash
conda install -c conda-forge nexios
```

### 4. **Using `poetry`** (Python Dependency Management and Packaging)

For projects managed with `poetry`, use this command to add Nexios to your dependencies:

```bash
poetry add nexios
```

### 5. **From `git`** (Install directly from the Git repository)

If you want to install Nexios directly from its Git repository (for example, if you need the latest code or want to contribute), you can use this command:

```bash
pip install git+https://github.com/nexios-labs/nexios.git
```

---

## Features

- [x] **Routing**
- [x] **Automatic OpenAPI Documentation**
- [x] **Session Management**
- [x] **File Router**
- [x] **Authentication (Limited)**
- [x] **Event Listener for Signals (Similar to Blinker)**
- [x] **Middleware Support**
- [x] **Express-like Functionality**
- [x] **JWT Authentication**
- [x] **Pydantic Support**
- [x] **In-built Support for CORS**
- [x] **Custom Decorators**
- [x] **WebSocket Support**
- [x] **Custom Error Handling**
- [x] **Pagination**

### Upcoming Features

- [ ] **Database ORM Integration**
- [ ] **Asynchronous Task Queue**
- [ ] **Rate Limiting**
- [ ] **API Throttling**

### Basic Example

```py

from typing import List, Optional
from uuid import uuid4, UUID
from pydantic import BaseModel
from nexios import get_application
from nexios.exceptions import HTTPException
from nexios.http import Request, Response
from nexios.routing import Router
from pydantic import ValidationError

# Create the app
app = get_application()

async def handle_validation_error(request: Request, response: Response, err: ValidationError):
    return response.json(err.errors(), status_code=400)

app.add_exception_handler(ValidationError, handle_validation_error)

# Create a router for our API with a prefix
api_router = Router(prefix="/api")

# Pydantic models for data validation
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

# In-memory "database"
tasks_db: List[Task] = []

# Startup handler to initialize some sample data
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

# Routes
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

@api_router.get("/tasks/{task_id}", responses=Task, tags=["tasks"], request_model=TaskCreate)
async def get_task(request: Request, response: Response):
    """Get a specific task by ID"""
    task_id = UUID(request.path_params["task_id"])
    for task in tasks_db:
        if task.id == task_id:
            return response.json(task)
    raise HTTPException(status_code=404, detail="Task not found")

@api_router.put("/tasks/{task_id}", responses=Task, tags=["tasks"], request_model=TaskCreate)
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
                completed=task.completed  # Preserve completion status
            )
            tasks_db[idx] = updated_task
            return response.json(updated_task)
    raise HTTPException(status_code=404, detail="Task not found")

@api_router.patch("/tasks/{task_id}/complete", responses=Task, tags=["tasks"], request_model=TaskCreate)
async def complete_task(request: Request, response: Response):
    """Mark a task as completed"""
    task_id = UUID(request.path_params["task_id"])
    for idx, task in enumerate(tasks_db):
        if task.id == task_id:
            updated_task = Task(
                id=task_id,
                title=task.title,
                description=task.description,
                completed=True
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

# Mount the API router
app.mount_router(api_router)

# Add a simple root route
@app.get("/")
async def root(request: Request, response: Response):
    return response.json({"message": "Task Manager API is running"})

# Shutdown handler
@app.on_shutdown
async def cleanup():
    print("Shutting down task manager...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
```

Visit http://localhost:4000/docs to view the Swagger API documentation.

<p>

<p align="center">
  <img src="./docs/_media/openapi.jpg"width="" height="" alt="Open APi"/>
</p>

### Testimonies

> "Adopting Nexios at our startup has been a practical and effective choice. In a fast-moving development environment, we needed something lightweight and efficient — Nexios met that need.
>
> Its clean architecture and compatibility with different ORMs helped our team work more efficiently and keep things maintainable. One of its strengths is how straightforward it is — minimal overhead, just the tools we need to build and scale our backend services.
>
> Credit to Dunamis for introducing Nexios to the team. It’s now a steady part of our stack, and it’s serving us well.
> — Joseph Mmadubuike , Chief Technology Officer buzzbuntu.com

## See the full docs

👉 <a href="https://nexios-labs.gitbook.io/nexios">https://nexios-labs.gitbook.io/nexios</a>

Sure thing, Dunamis! Here's a well-written **"Donate"** section for Nexios with more context, purpose, and a call to action. You can just replace the link with your actual Buy Me a Coffee profile:

---

## ☕ Donate to Support Nexios

Nexios is a passion project built to make backend development in Python faster, cleaner, and more developer-friendly. It’s fully open-source and maintained with love, late nights, and lots of coffee.

If Nexios has helped you build something awesome, saved you time, or inspired your next project, consider supporting its continued development. Your donation helps cover hosting, documentation tools, and fuels new features and updates.

Every little bit counts — whether it's the cost of a coffee or more. Thank you for believing in the project!

👉 [**Buy Me a Coffee**](https://www.buymeacoffee.com/techwithdul) and support the future of Nexios.
