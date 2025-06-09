# 🚀 Day 12: File Uploads

## File Upload Basics

Handling basic file uploads:

```python
from nexios import get_application
from nexios.http import Request, Response, UploadFile
from nexios.responses import FileResponse
from pathlib import Path
import aiofiles
import shutil

app = get_application()

# Configure upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile):
    # Save file to disk
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
async def upload_multiple_files(files: list[UploadFile]):
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
async def download_file(filename: str):
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        return Response(
            content={"error": "File not found"},
            status_code=404
        )
    
    return FileResponse(file_path)
```

## Multipart Form Data

Handling file uploads with additional form data:

```python
from nexios.forms import Form, FormField
from typing import Optional
from datetime import datetime

class FileUploadForm(Form):
    file: UploadFile
    description: str = FormField(max_length=500)
    category: Optional[str] = None
    tags: list[str] = FormField(default_factory=list)

@app.post("/upload-with-data")
async def upload_with_data(form: FileUploadForm):
    # Save file
    file_path = UPLOAD_DIR / form.file.filename
    
    async with aiofiles.open(file_path, "wb") as f:
        content = await form.file.read()
        await f.write(content)
    
    # Save metadata
    metadata = {
        "filename": form.file.filename,
        "description": form.description,
        "category": form.category,
        "tags": form.tags,
        "uploaded_at": datetime.now().isoformat(),
        "size": len(content),
        "content_type": form.file.content_type
    }
    
    # Store metadata (implement your storage)
    await store_file_metadata(metadata)
    
    return metadata

# Image upload with thumbnail
from PIL import Image
import io

class ImageUploadForm(Form):
    image: UploadFile
    generate_thumbnail: bool = FormField(default=True)
    max_size: tuple[int, int] = FormField(
        default=(800, 800)
    )

@app.post("/upload-image")
async def upload_image(form: ImageUploadForm):
    # Validate image
    content = await form.image.read()
    image = Image.open(io.BytesIO(content))
    
    # Resize if needed
    if form.generate_thumbnail:
        image.thumbnail(form.max_size)
        
        # Save thumbnail
        thumb_path = UPLOAD_DIR / f"thumb_{form.image.filename}"
        image.save(thumb_path)
    
    # Save original
    file_path = UPLOAD_DIR / form.image.filename
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    return {
        "original": form.image.filename,
        "thumbnail": f"thumb_{form.image.filename}" if form.generate_thumbnail else None,
        "dimensions": image.size
    }
```

## File Validation

Implementing file validation:

```python
from nexios.validation import FileValidator
import magic
import hashlib

class FileTypeValidator:
    def __init__(self, allowed_types: list[str]):
        self.allowed_types = allowed_types
    
    async def validate(self, file: UploadFile) -> bool:
        content = await file.read()
        mime = magic.from_buffer(content, mime=True)
        
        # Reset file position
        await file.seek(0)
        
        return mime in self.allowed_types

class FileSizeValidator:
    def __init__(self, max_size: int):  # max_size in bytes
        self.max_size = max_size
    
    async def validate(self, file: UploadFile) -> bool:
        content = await file.read()
        size = len(content)
        
        # Reset file position
        await file.seek(0)
        
        return size <= self.max_size

@app.post("/upload-validated")
async def upload_validated(file: UploadFile):
    # Configure validators
    type_validator = FileTypeValidator([
        "image/jpeg",
        "image/png",
        "application/pdf"
    ])
    
    size_validator = FileSizeValidator(
        max_size=5 * 1024 * 1024  # 5MB
    )
    
    # Validate file type
    if not await type_validator.validate(file):
        return Response(
            content={"error": "Invalid file type"},
            status_code=400
        )
    
    # Validate file size
    if not await size_validator.validate(file):
        return Response(
            content={"error": "File too large"},
            status_code=400
        )
    
    # Calculate hash for deduplication
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Check if file already exists
    if await file_exists(file_hash):
        return Response(
            content={"error": "File already exists"},
            status_code=409
        )
    
    # Save file
    file_path = UPLOAD_DIR / f"{file_hash}_{file.filename}"
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    return {
        "filename": file.filename,
        "hash": file_hash,
        "path": str(file_path)
    }
```

## Storage Options

Implementing different storage backends:

```python
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
import boto3
from google.cloud import storage

class StorageBackend(ABC):
    @abstractmethod
    async def save(
        self,
        file: BinaryIO,
        path: str,
        content_type: Optional[str] = None
    ) -> str:
        pass
    
    @abstractmethod
    async def get(self, path: str) -> BinaryIO:
        pass
    
    @abstractmethod
    async def delete(self, path: str) -> bool:
        pass

class LocalStorage(StorageBackend):
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
    
    async def save(
        self,
        file: BinaryIO,
        path: str,
        content_type: Optional[str] = None
    ) -> str:
        full_path = self.base_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(file.read())
        
        return str(full_path)
    
    async def get(self, path: str) -> BinaryIO:
        full_path = self.base_dir / path
        return open(full_path, "rb")
    
    async def delete(self, path: str) -> bool:
        full_path = self.base_dir / path
        try:
            full_path.unlink()
            return True
        except FileNotFoundError:
            return False

class S3Storage(StorageBackend):
    def __init__(
        self,
        bucket: str,
        aws_access_key: str,
        aws_secret_key: str,
        region: str = "us-east-1"
    ):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        self.bucket = bucket
    
    async def save(
        self,
        file: BinaryIO,
        path: str,
        content_type: Optional[str] = None
    ) -> str:
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
        
        self.s3.upload_fileobj(
            file,
            self.bucket,
            path,
            ExtraArgs=extra_args
        )
        
        return f"s3://{self.bucket}/{path}"
    
    async def get(self, path: str) -> BinaryIO:
        response = self.s3.get_object(
            Bucket=self.bucket,
            Key=path
        )
        return response["Body"]
    
    async def delete(self, path: str) -> bool:
        try:
            self.s3.delete_object(
                Bucket=self.bucket,
                Key=path
            )
            return True
        except:
            return False

# Use storage backend
storage = LocalStorage(UPLOAD_DIR)
# Or use S3
# storage = S3Storage(
#     bucket="my-bucket",
#     aws_access_key="key",
#     aws_secret_key="secret"
# )

@app.post("/upload-storage")
async def upload_to_storage(file: UploadFile):
    content = await file.read()
    path = f"uploads/{file.filename}"
    
    url = await storage.save(
        io.BytesIO(content),
        path,
        file.content_type
    )
    
    return {"url": url}
```

## 📝 Practice Exercise

1. Build a file upload system:
   - Multiple file upload
   - Progress tracking
   - Chunked upload
   - Resume support

2. Implement file processing:
   - Image resizing
   - Format conversion
   - Metadata extraction
   - Virus scanning

3. Create a file management API:
   - List files
   - Search files
   - Share files
   - Access control

## 📚 Additional Resources
- [File Handling Guide](https://nexios.dev/guide/files)
- [Storage Options](https://nexios.dev/guide/storage)
- [Security Best Practices](https://nexios.dev/guide/security)
- [Cloud Storage Integration](https://nexios.dev/guide/cloud)

## 🎯 Next Steps
Tomorrow in [Day 13: WebSocket Basics](../day13/index.md), we'll explore:
- WebSocket setup
- Connection handling
- Message types
- Error handling