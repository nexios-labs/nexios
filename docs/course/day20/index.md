# Day 20: Concurrency and Async Utilities

## Learning Objectives
- Master Nexios's concurrency utilities
- Understand task groups and background tasks
- Work with async events and lazy loading
- Implement thread pool execution

## Task Groups

Nexios provides a powerful `TaskGroup` class for managing multiple tasks:

```python
from nexios import NexiosApp
from nexios.utils.concurrency import TaskGroup, create_task_group
import asyncio

app = NexiosApp()

@app.get("/process")
async def process_items(request, response):
    async with TaskGroup() as group:
        # Create multiple tasks
        task1 = group.create_task(process_item(1))
        task2 = group.create_task(process_item(2))
        task3 = group.create_task(process_item(3))
        
        # Tasks are automatically managed and cleaned up
        results = await asyncio.gather(task1, task2, task3)
        return {"results": results}

# Alternative using context manager
@app.get("/process-alt")
async def process_items_alt(request, response):
    results = []
    async for group in create_task_group():
        task1 = group.create_task(process_item(1))
        task2 = group.create_task(process_item(2))
        results = await asyncio.gather(task1, task2)
    return {"results": results}
```

## Background Tasks

Nexios provides a `create_background_task` context manager for managing long-running tasks:

```python
from nexios.utils.concurrency import create_background_task
import asyncio

@app.get("/start-job")
async def start_background_job(request, response):
    async def long_running_job():
        while True:
            await asyncio.sleep(60)
            # Do some work
            
    async with create_background_task(long_running_job()) as task:
        # Task is running in background and will be cancelled on context exit
        return {"job_id": id(task)}

# Run multiple tasks until first completes
@app.get("/race")
async def race_tasks(request, response):
    async def task1():
        await asyncio.sleep(1)
        return "Task 1 won!"
        
    async def task2():
        await asyncio.sleep(2)
        return "Task 2 won!"
    
    result = await run_until_first_complete(
        task1,
        (task2, {})  # With kwargs
    )
    return {"winner": result}
```

## Thread Pool Execution

For CPU-bound tasks, use the thread pool executor:

```python
from nexios.utils.concurrency import run_in_threadpool
import time

def cpu_intensive_task(n: int) -> int:
    # Simulate CPU-intensive work
    time.sleep(1)
    return n * n

@app.get("/compute/{n:int}")
async def compute(request, response):
    # Run CPU-intensive task in thread pool
    result = await run_in_threadpool(
        cpu_intensive_task,
        request.path_params.n
    )
    return {"result": result}
```

## Async Events

Nexios provides an `AsyncEvent` class for coordinating coroutines:

```python
from nexios.utils.concurrency import AsyncEvent
import asyncio

class JobCoordinator:
    def __init__(self):
        self.completion_event = AsyncEvent()
        self.result = None
        
    async def run_job(self):
        # Simulate work
        await asyncio.sleep(5)
        self.result = "Job completed"
        self.completion_event.set()
        
    async def wait_for_completion(self):
        await self.completion_event.wait()
        return self.result

@app.get("/coordinated-job")
async def run_coordinated_job(request, response):
    coordinator = JobCoordinator()
    
    # Start job in background
    asyncio.create_task(coordinator.run_job())
    
    # Wait for completion
    result = await coordinator.wait_for_completion()
    return {"result": result}
```

## Lazy Async Values

The `AsyncLazy` class helps with lazy computation of expensive values:

```python
from nexios.utils.concurrency import AsyncLazy
import asyncio

async def expensive_computation():
    await asyncio.sleep(2)  # Simulate expensive work
    return {"data": "expensive result"}

# Create lazy value
lazy_data = AsyncLazy(expensive_computation)

@app.get("/data")
async def get_data(request, response):
    # Value is computed only when needed
    data = await lazy_data.get()
    return data

@app.post("/reset")
async def reset_data(request, response):
    # Reset so value will be recomputed next time
    lazy_data.reset()
    return {"status": "reset"}
```

## 📝 Practice Exercise

1. Build a Task Management System:
   ```python
   from nexios import NexiosApp
   from nexios.utils.concurrency import (
       TaskGroup,
       create_background_task,
       AsyncEvent,
       run_in_threadpool
   )
   
   app = NexiosApp()
   
   class TaskManager:
       def __init__(self):
           self.tasks = {}
           self.events = {}
           
       async def create_task(self, task_id: str, duration: int):
           async def task():
               try:
                   # Simulate work
                   await asyncio.sleep(duration)
                   self.events[task_id].set()
               except asyncio.CancelledError:
                   self.events[task_id].clear()
                   raise
           
           self.events[task_id] = AsyncEvent()
           async with create_background_task(task()) as t:
               self.tasks[task_id] = t
               return {"status": "started"}
               
       async def wait_for_task(self, task_id: str):
           if task_id not in self.events:
               return {"error": "Task not found"}
           
           await self.events[task_id].wait()
           return {"status": "completed"}
   
   manager = TaskManager()
   
   @app.post("/tasks")
   async def create_task(request, response):
       data = await request.json
       return await manager.create_task(
           data["task_id"],
           data["duration"]
       )
   
   @app.get("/tasks/{task_id}")
   async def get_task(request, response):
       return await manager.wait_for_task(
           request.path_params.task_id
       )
   ```

2. Implement a Parallel Processing Pipeline:
   - Use task groups for parallel processing
   - Coordinate with async events
   - Handle CPU-bound tasks with thread pool
   - Implement lazy loading for results

3. Create a Resource Manager:
   - Manage multiple background tasks
   - Implement graceful shutdown
   - Handle task cancellation
   - Monitor task status

## 📚 Additional Resources
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [ASGI Specification](https://asgi.readthedocs.io/en/latest/)
- [Nexios Concurrency Guide](../../guide/concurrency.md)
- [Threading vs Asyncio](https://realpython.com/python-concurrency/)

## 🎯 Next Steps
Tomorrow in [Day 21: Project: Chat Application](../day21/index.md), we'll explore:
- Real-time messaging
- User presence
- Message persistence
- Notifications