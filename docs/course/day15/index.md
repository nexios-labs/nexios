# 🚀 Day 15: Background Tasks

## Task Queues

Setting up task queues for background processing:

```python
from nexios import get_application
from nexios.tasks import (
    TaskQueue,
    Task,
    TaskStatus,
    BackgroundTask
)
from typing import Optional, Any
import asyncio
from datetime import datetime

app = get_application()

# Configure task queue
queue = TaskQueue()

class EmailTask(Task):
    def __init__(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: Optional[list] = None
    ):
        self.to = to
        self.subject = subject
        self.body = body
        self.attachments = attachments or []
    
    async def execute(self) -> Any:
        # Simulate email sending
        await asyncio.sleep(2)
        return {
            "to": self.to,
            "subject": self.subject,
            "sent_at": datetime.now().isoformat()
        }

@app.post("/send-email")
async def send_email(
    to: str,
    subject: str,
    body: str
):
    # Create and queue task
    task = EmailTask(to, subject, body)
    task_id = await queue.enqueue(task)
    
    return {
        "task_id": task_id,
        "status": "queued"
    }

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    task = await queue.get_task(task_id)
    
    if not task:
        return {"error": "Task not found"}
    
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.status == TaskStatus.COMPLETED else None,
        "error": str(task.error) if task.error else None
    }
```

## Async Workers

Implementing async task workers:

```python
from nexios.workers import Worker, WorkerPool
from nexios.cache import RedisCache
import signal
import sys

class TaskWorker(Worker):
    def __init__(self, queue: TaskQueue):
        self.queue = queue
        self.running = True
        self.current_task: Optional[Task] = None
    
    async def start(self):
        # Handle shutdown signals
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self.handle_shutdown)
        
        while self.running:
            try:
                # Get next task
                task = await self.queue.dequeue()
                if not task:
                    await asyncio.sleep(1)
                    continue
                
                self.current_task = task
                
                # Execute task
                try:
                    result = await task.execute()
                    await self.queue.complete_task(
                        task.id,
                        result
                    )
                except Exception as e:
                    await self.queue.fail_task(
                        task.id,
                        str(e)
                    )
                
                self.current_task = None
            
            except Exception as e:
                print(f"Worker error: {e}")
                await asyncio.sleep(1)
    
    def handle_shutdown(self, signum, frame):
        print("Shutting down worker...")
        self.running = False
        
        if self.current_task:
            asyncio.create_task(
                self.queue.requeue_task(
                    self.current_task.id
                )
            )

# Worker pool for parallel processing
class AsyncWorkerPool:
    def __init__(
        self,
        queue: TaskQueue,
        num_workers: int = 4
    ):
        self.queue = queue
        self.num_workers = num_workers
        self.workers: List[TaskWorker] = []
    
    async def start(self):
        for _ in range(self.num_workers):
            worker = TaskWorker(self.queue)
            self.workers.append(worker)
            asyncio.create_task(worker.start())
    
    async def stop(self):
        for worker in self.workers:
            worker.running = False

# Start worker pool
worker_pool = AsyncWorkerPool(queue)

@app.on_event("startup")
async def start_workers():
    await worker_pool.start()

@app.on_event("shutdown")
async def stop_workers():
    await worker_pool.stop()
```

## Scheduled Tasks

Managing scheduled and recurring tasks:

```python
from nexios.scheduler import Scheduler, CronJob
from datetime import timedelta

scheduler = Scheduler()

# Schedule one-time task
@scheduler.schedule(
    delay=timedelta(hours=1)
)
async def cleanup_old_files():
    # Implement cleanup logic
    pass

# Schedule recurring task
@scheduler.schedule(
    cron="0 0 * * *"  # Daily at midnight
)
async def daily_report():
    # Generate and send report
    pass

# Dynamic scheduling
class BackupJob(CronJob):
    def __init__(self, backup_path: str):
        self.backup_path = backup_path
    
    async def execute(self):
        # Perform backup
        pass

@app.post("/schedule-backup")
async def schedule_backup(
    path: str,
    schedule: str  # Cron expression
):
    job = BackupJob(path)
    job_id = await scheduler.add_job(
        job,
        schedule
    )
    
    return {
        "job_id": job_id,
        "schedule": schedule
    }

@app.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    await scheduler.remove_job(job_id)
    return {"message": "Job cancelled"}

# Start scheduler
@app.on_event("startup")
async def start_scheduler():
    await scheduler.start()

@app.on_event("shutdown")
async def stop_scheduler():
    await scheduler.stop()
```

## Progress Tracking

Implementing task progress tracking:

```python
from nexios.progress import ProgressTracker
from typing import AsyncIterator

class ProgressTask(Task):
    def __init__(self):
        self.progress = ProgressTracker()
    
    async def execute(self) -> Any:
        total_steps = 10
        self.progress.set_total(total_steps)
        
        for i in range(total_steps):
            # Do work
            await asyncio.sleep(1)
            
            # Update progress
            self.progress.advance(1)
            self.progress.set_message(
                f"Processing step {i + 1}/{total_steps}"
            )
        
        return {"status": "completed"}

class FileProcessor(Task):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.progress = ProgressTracker()
    
    async def process_chunks(self) -> AsyncIterator[bytes]:
        chunk_size = 8192
        total_size = 0
        
        async with aiofiles.open(self.file_path, "rb") as f:
            while chunk := await f.read(chunk_size):
                total_size += len(chunk)
                self.progress.set_total(total_size)
                yield chunk
    
    async def execute(self) -> Any:
        processed = 0
        
        async for chunk in self.process_chunks():
            # Process chunk
            await self.process_chunk(chunk)
            
            processed += len(chunk)
            self.progress.update(processed)
            
            # Update processing rate
            rate = processed / (time.time() - self.start_time)
            self.progress.set_message(
                f"Processing at {rate:.2f} bytes/sec"
            )
        
        return {"bytes_processed": processed}

@app.post("/process-file")
async def process_file(file: UploadFile):
    # Save file
    file_path = f"uploads/{file.filename}"
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(await file.read())
    
    # Create and queue task
    task = FileProcessor(file_path)
    task_id = await queue.enqueue(task)
    
    return {
        "task_id": task_id,
        "status": "processing"
    }

@app.get("/task/{task_id}/progress")
async def get_task_progress(task_id: str):
    task = await queue.get_task(task_id)
    
    if not task:
        return {"error": "Task not found"}
    
    if not hasattr(task, "progress"):
        return {"error": "Task doesn't support progress tracking"}
    
    return {
        "task_id": task_id,
        "status": task.status,
        "progress": {
            "current": task.progress.current,
            "total": task.progress.total,
            "percentage": task.progress.percentage,
            "message": task.progress.message
        }
    }
```

## 📝 Practice Exercise

1. Build a task processing system:
   - Multiple queues
   - Priority levels
   - Retry mechanisms
   - Dead letter queue

2. Implement scheduled tasks:
   - Recurring jobs
   - Dynamic scheduling
   - Job dependencies
   - Error handling

3. Create a progress system:
   - Real-time updates
   - Progress estimation
   - Cancel support
   - Detailed stats

## 📚 Additional Resources
- [Task Queue Guide](https://nexios.dev/guide/tasks)
- [Scheduling Guide](https://nexios.dev/guide/scheduler)
- [Progress Tracking](https://nexios.dev/guide/progress)
- [Worker Management](https://nexios.dev/guide/workers)

## 🎯 Next Steps
Tomorrow in [Day 16: Error Handling](../day16/index.md), we'll explore:
- Exception handling
- Error responses
- Logging
- Monitoring