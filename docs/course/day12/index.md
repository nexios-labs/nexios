# 🚀 Day 12: File Uploads

## File Upload Basics

Handling basic file uploads:

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from pathlib import Path
import aiofiles
import shutil

app = NexiosApp()

# Configure upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_file(request :Request, response :Response):
    files = await request.files
    file = files.get("file")
    file_path = UPLOAD_DIR / file.filename
    
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content)
    }

@app.post("/upload-multiple")
async def upload_multiple_files(request :Request, response :Response):
    files = await request.files
    results = []
    
    for file in files:
        file_path = UPLOAD_DIR / file.filename
        
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        
        results.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content)
        })
    
    return {"files": results}

@app.get("/files/{filename}")
async def download_file(request :Request, response :Response,filename: str):
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        return response.json(
            {"error": "File not found"},
            status_code=404
        )
    
    return response.file(file_path)
```

## Multipart Form Data

Handling file uploads with additional form data:

```python
from typing import Optional
from datetime import datetime


@app.post("/upload-with-data")
async def upload_with_data(request :Request, response :Response):
    form = await request.form
    file = form.get("file")
    file_path = UPLOAD_DIR / file.filename
    
    async with aiofiles.open(file_path, "wb") as f:
        content = await form.file.read()
        await f.write(content)
    
    # Save metadata
    metadata = {
        "filename": file.filename,
        "description": description,
        "category": category,
        "tags": tags,
        "uploaded_at": datetime.now().isoformat(),
        "size": len(content),
        "content_type": file.content_type
    }
    
    # Store metadata (implement your storage)
    await store_file_metadata(metadata)
    
    return metadata


```

