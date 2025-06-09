# 🚀 Day 7: Project – Mini To-Do API

## Project Overview

Today we'll build a complete To-Do API with the following features:
- CRUD operations for tasks
- JSON data storage
- Basic authentication
- Request validation
- Error handling middleware

## Project Structure

```
todo-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── middleware.py
│   └── storage.py
├── .env
└── requirements.txt
```

## Implementation

### 1. Models (models.py)

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
```

### 2. Storage (storage.py)

```python
import json
from typing import Dict, List, Optional
from uuid import UUID
from .models import Task
import os

class JSONStorage:
    def __init__(self, file_path: str = "tasks.json"):
        self.file_path = file_path
        self.tasks: Dict[str, Task] = {}
        self.load()
    
    def load(self) -> None:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                data = json.load(f)
                self.tasks = {
                    k: Task(**v) for k, v in data.items()
                }
    
    def save(self) -> None:
        with open(self.file_path, "w") as f:
            json.dump(
                {k: v.dict() for k, v in self.tasks.items()},
                f,
                default=str,
                indent=2
            )
    
    def get_all(self) -> List[Task]:
        return list(self.tasks.values())
    
    def get_by_id(self, task_id: UUID) -> Optional[Task]:
        return self.tasks.get(str(task_id))
    
    def create(self, task: Task) -> Task:
        self.tasks[str(task.id)] = task
        self.save()
        return task
    
    def update(self, task_id: UUID, task: Task) -> Optional[Task]:
        if str(task_id) in self.tasks:
            self.tasks[str(task_id)] = task
            self.save()
            return task
        return None
    
    def delete(self, task_id: UUID) -> bool:
        if str(task_id) in self.tasks:
            del self.tasks[str(task_id)]
            self.save()
            return True
        return False
```

### 3. Middleware (middleware.py)

```python
from nexios import get_application
from nexios.http import Request, Response
from nexios.types import Middleware
import time

async def timing_middleware(
    request: Request,
    response: Response,
    call_next: Middleware
) -> Response:
    start_time = time.time()
    response = await call_next()
    process_time = time.time() - start_time
    response.set_header("X-Process-Time",str(process_time))
    return response

async def error_middleware(
    request: Request,
    response: Response,
    call_next: Middleware
) -> Response:
    try:
        return await call_next()
    except Exception as e:
        return response.json(
            content={
                "error": str(e),
                "type": e.__class__.__name__
            },
            status_code=500
        )
```

### 4. Routes (routes.py)

```python
from nexios import Router
from nexios.http import Response
from nexios import status
from .models import Task, TaskCreate, TaskUpdate
from .storage import JSONStorage
from datetime import datetime
from uuid import UUID

router = Router(prefix="/api/tasks")
storage = JSONStorage()

@router.get("/")
async def list_tasks(request: Request, response: Response):
    tasks = storage.get_all()
    return {
        "total": len(tasks),
        "tasks": tasks
    }

@router.post("/")
async def create_task(request: Request, response: Response):
    data  = await req.json
    task = Task(
      **data
    )
    created_task = storage.create(task)
    return response.json(
        content=created_task.dict(),
        status_code=status.HTTP_201_CREATED
    )

@router.get("/{task_id}")
async def get_task(request: Request, response: Response,task_id: UUID):
    task = storage.get_by_id(task_id)
    if not task:
        return response.json(
            content={"error": "Task not found"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    return task

@router.put("/{task_id}")
async def update_task(task_id: UUID, data: TaskUpdate):
    task = storage.get_by_id(task_id)
    if not task:
        return response.json(
            content={"error": "Task not found"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Update fields
    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.completed is not None:
        task.completed = data.completed
    
    task.updated_at = datetime.utcnow()
    updated_task = storage.update(task_id, task)
    
    return updated_task

@router.delete("/{task_id}")
async def delete_task(task_id: UUID):
    if storage.delete(task_id):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(
        content={"error": "Task not found"},
        status_code=status.HTTP_404_NOT_FOUND
    )
```

### 5. Main Application (main.py)

```python
from nexios import get_application
from .routes import router
from .middleware import timing_middleware, error_middleware

app = get_application()

# Add middleware
app.add_middleware(timing_middleware)
app.add_middleware(error_middleware)

# Include routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

## Testing the API

### Using curl

```bash
# List tasks
curl http://localhost:8000/api/tasks

# Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Nexios", "description": "Complete the course"}'

# Get task
curl http://localhost:8000/api/tasks/{task_id}

# Update task
curl -X PUT http://localhost:8000/api/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete task
curl -X DELETE http://localhost:8000/api/tasks/{task_id}
```

## 📝 Practice Exercise

Extend the To-Do API with:

1. Task Categories:
   - Add category field to tasks
   - Filter tasks by category
   - Category statistics

2. Due Dates:
   - Add due_date field
   - Overdue task detection
   - Task reminders

3. Task Priority:
   - Add priority levels
   - Sort by priority
   - Priority-based filtering


## 🎯 Next Steps
Next week in [Day 8: JWT Auth (Part 1)](../day08/index.md), we'll explore:
- JWT authentication basics
- Token creation and verification
- Protected endpoints