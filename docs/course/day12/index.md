# Day 12: Security

Welcome to Day 12! Today we'll learn about implementing security best practices in Nexios applications.

## Understanding Security

Key security aspects:
- Authentication & Authorization
- Input validation
- CSRF protection
- XSS prevention
- SQL injection prevention
- Rate limiting
- Security headers
- Data encryption
- Audit logging

## Security Headers Middleware

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from typing import Callable

app = NexiosApp()

async def security_headers_middleware(
    request: Request,
    response: Response,
    call_next: Callable
):
    response = await call_next()
    
    # Security headers
    response.headers.update({
        # Prevent clickjacking
        "X-Frame-Options": "DENY",
        
        # XSS protection
        "X-XSS-Protection": "1; mode=block",
        
        # MIME type sniffing prevention
        "X-Content-Type-Options": "nosniff",
        
        # HSTS (force HTTPS)
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        
        # Content Security Policy
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'"
        ),
        
        # Referrer Policy
        "Referrer-Policy": "strict-origin-when-cross-origin",
        
        # Feature Policy
        "Permissions-Policy": (
            "camera=(), "
            "microphone=(), "
            "geolocation=()"
        )
    })
    
    return response

app.add_middleware(security_headers_middleware)
```

## Input Validation

```python
from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
import re

class UserInput(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)
    
    @validator("password")
    def password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain special character")
        return v

@app.post("/users")
async def create_user(request: Request, response: Response):
    try:
        data = await request.json()
        user_input = UserInput(**data)
        
        # Process validated input...
        
    except ValidationError as e:
        return response.json({
            "error": "Validation error",
            "details": e.errors()
        }, status_code=422)
```

## Rate Limiting

```python
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List
import asyncio

@dataclass
class RateLimit:
    requests: int
    window: int  # seconds

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    async def is_allowed(
        self,
        key: str,
        limit: RateLimit
    ) -> bool:
        now = time.time()
        
        # Remove old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < limit.window
        ]
        
        # Check limit
        if len(self.requests[key]) >= limit.requests:
            return False
        
        # Add new request
        self.requests[key].append(now)
        return True
    
    def get_remaining(
        self,
        key: str,
        limit: RateLimit
    ) -> int:
        now = time.time()
        valid_requests = [
            req_time for req_time in self.requests[key]
            if now - req_time < limit.window
        ]
        return limit.requests - len(valid_requests)

rate_limiter = RateLimiter()

async def rate_limit_middleware(
    request: Request,
    response: Response,
    call_next: Callable,
    limit: RateLimit = RateLimit(100, 60)  # 100 requests per minute
):
    # Get client IP
    client_ip = request.client.host
    
    # Check rate limit
    if not await rate_limiter.is_allowed(client_ip, limit):
        return response.json({
            "error": "Rate limit exceeded",
            "retry_after": limit.window
        }, status_code=429)
    
    response = await call_next()
    
    # Add rate limit headers
    remaining = rate_limiter.get_remaining(client_ip, limit)
    response.headers.update({
        "X-RateLimit-Limit": str(limit.requests),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(time.time() + limit.window))
    })
    
    return response

app.add_middleware(rate_limit_middleware)
```

## CSRF Protection

```python
import secrets
from typing import Optional

class CSRFProtection:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def generate_token(self) -> str:
        return secrets.token_urlsafe(32)
    
    def validate_token(
        self,
        request_token: Optional[str],
        session_token: Optional[str]
    ) -> bool:
        if not request_token or not session_token:
            return False
        return secrets.compare_digest(request_token, session_token)

csrf = CSRFProtection(secret_key="your-secret-key")

async def csrf_middleware(request: Request, response: Response, call_next: Callable):
    if request.method in {"POST", "PUT", "DELETE", "PATCH"}:
        # Get tokens
        request_token = request.headers.get("X-CSRF-Token")
        session_token = request.session.get("csrf_token")
        
        # Validate token
        if not csrf.validate_token(request_token, session_token):
            return response.json({
                "error": "Invalid CSRF token"
            }, status_code=403)
    
    response = await call_next()
    
    # Set new token for GET requests
    if request.method == "GET":
        token = csrf.generate_token()
        request.session["csrf_token"] = token
        response.headers["X-CSRF-Token"] = token
    
    return response

app.add_middleware(csrf_middleware)
```

## SQL Injection Prevention

```python
from sqlalchemy import text
from databases import Database

database = Database("postgresql://user:pass@localhost/db")

async def safe_query(query: str, params: dict):
    """Execute a safe parameterized query"""
    return await database.fetch_all(
        query=text(query),
        values=params
    )

# UNSAFE:
# f"SELECT * FROM users WHERE username = '{username}'"

# SAFE:
async def get_user(username: str):
    query = "SELECT * FROM users WHERE username = :username"
    return await safe_query(query, {"username": username})
```

## Password Security

```python
import bcrypt
from cryptography.fernet import Fernet
import base64
from typing import Tuple

class PasswordManager:
    def __init__(self, encryption_key: bytes):
        self.fernet = Fernet(encryption_key)
    
    def hash_password(self, password: str) -> Tuple[bytes, bytes]:
        """Hash password and return (salt, hash)"""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(
            password.encode(),
            salt
        )
        return salt, password_hash
    
    def verify_password(
        self,
        password: str,
        password_hash: bytes,
        salt: bytes
    ) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            password.encode(),
            password_hash
        )
    
    def encrypt_sensitive_data(self, data: str) -> bytes:
        """Encrypt sensitive data"""
        return self.fernet.encrypt(data.encode())
    
    def decrypt_sensitive_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data"""
        return self.fernet.decrypt(encrypted_data).decode()

# Usage
key = Fernet.generate_key()
password_manager = PasswordManager(key)

# Store password
password = "MySecurePassword123!"
salt, password_hash = password_manager.hash_password(password)

# Verify password
is_valid = password_manager.verify_password(
    password,
    password_hash,
    salt
)

# Encrypt sensitive data
sensitive_data = "1234-5678-9012-3456"
encrypted = password_manager.encrypt_sensitive_data(sensitive_data)
decrypted = password_manager.decrypt_sensitive_data(encrypted)
```

## Audit Logging

```python
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import json
import uuid

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # Add file handler
        handler = logging.FileHandler("audit.log")
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(message)s'
            )
        )
        self.logger.addHandler(handler)
    
    def log_event(
        self,
        event_type: str,
        user_id: Optional[str],
        action: str,
        resource: str,
        status: str,
        details: Dict[str, Any] = None
    ):
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details or {}
        }
        
        self.logger.info(json.dumps(event))
        return event

audit_logger = AuditLogger()

async def audit_middleware(request: Request, response: Response, call_next: Callable):
    start_time = datetime.utcnow()
    
    try:
        response = await call_next()
        
        # Log successful request
        audit_logger.log_event(
            event_type="request",
            user_id=getattr(request.state, "user_id", None),
            action=request.method,
            resource=request.url.path,
            status="success",
            details={
                "status_code": response.status_code,
                "duration": (datetime.utcnow() - start_time).total_seconds(),
                "ip_address": request.client.host,
                "user_agent": request.headers.get("User-Agent")
            }
        )
        
        return response
        
    except Exception as e:
        # Log error
        audit_logger.log_event(
            event_type="error",
            user_id=getattr(request.state, "user_id", None),
            action=request.method,
            resource=request.url.path,
            status="error",
            details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "duration": (datetime.utcnow() - start_time).total_seconds(),
                "ip_address": request.client.host,
                "user_agent": request.headers.get("User-Agent")
            }
        )
        raise

app.add_middleware(audit_middleware)
```

## Mini-Project: Secure File Upload Service

```python
from nexios import NexiosApp
from nexios.http import Request, Response
import os
import magic
import hashlib
import uuid
from typing import Set, Dict
import aiofiles
import asyncio
import logging

# Configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
    "text/plain"
}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureFileUpload:
    def __init__(
        self,
        upload_dir: str,
        max_size: int,
        allowed_types: Set[str]
    ):
        self.upload_dir = upload_dir
        self.max_size = max_size
        self.allowed_types = allowed_types
        self.mime = magic.Magic(mime=True)
        
        # Create upload directory
        os.makedirs(upload_dir, exist_ok=True)
    
    async def save_file(
        self,
        file_data: bytes,
        original_filename: str
    ) -> Dict[str, str]:
        # Generate secure filename
        file_id = str(uuid.uuid4())
        extension = os.path.splitext(original_filename)[1]
        secure_filename = f"{file_id}{extension}"
        
        # Check file size
        if len(file_data) > self.max_size:
            raise ValueError("File too large")
        
        # Check file type
        file_type = self.mime.from_buffer(file_data)
        if file_type not in self.allowed_types:
            raise ValueError("File type not allowed")
        
        # Calculate hash
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        # Save file
        file_path = os.path.join(self.upload_dir, secure_filename)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_data)
        
        return {
            "id": file_id,
            "filename": secure_filename,
            "original_filename": original_filename,
            "size": len(file_data),
            "type": file_type,
            "hash": file_hash
        }

# Application setup
app = NexiosApp()
uploader = SecureFileUpload(
    upload_dir=UPLOAD_DIR,
    max_size=MAX_FILE_SIZE,
    allowed_types=ALLOWED_TYPES
)

# Rate limiter for uploads
upload_limiter = RateLimiter()
UPLOAD_LIMIT = RateLimit(10, 3600)  # 10 uploads per hour

@app.post("/upload")
async def upload_file(request: Request, response: Response):
    # Check rate limit
    client_ip = request.client.host
    if not await upload_limiter.is_allowed(client_ip, UPLOAD_LIMIT):
        return response.json({
            "error": "Upload limit exceeded"
        }, status_code=429)
    
    try:
        # Get file data
        form = await request.form()
        file = form.get("file")
        
        if not file:
            return response.json({
                "error": "No file provided"
            }, status_code=400)
        
        # Read file data
        file_data = await file.read()
        
        # Save file
        result = await uploader.save_file(
            file_data,
            file.filename
        )
        
        # Log upload
        audit_logger.log_event(
            event_type="file_upload",
            user_id=getattr(request.state, "user_id", None),
            action="upload",
            resource=f"/files/{result['id']}",
            status="success",
            details={
                "filename": result["original_filename"],
                "size": result["size"],
                "type": result["type"],
                "hash": result["hash"]
            }
        )
        
        return response.json(result, status_code=201)
        
    except ValueError as e:
        return response.json({
            "error": str(e)
        }, status_code=400)
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return response.json({
            "error": "Internal server error"
        }, status_code=500)

@app.get("/files/{file_id}")
async def get_file(request: Request, response: Response, file_id: str):
    try:
        # Find file
        files = os.listdir(UPLOAD_DIR)
        file_name = next(
            (f for f in files if f.startswith(file_id)),
            None
        )
        
        if not file_name:
            return response.json({
                "error": "File not found"
            }, status_code=404)
        
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        # Read and send file
        return await response.send_file(
            file_path,
            filename=file_name
        )
        
    except Exception as e:
        logger.error(f"File retrieval error: {str(e)}")
        return response.json({
            "error": "Internal server error"
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

## Key Concepts Learned

- Security headers
- Input validation
- Rate limiting
- CSRF protection
- SQL injection prevention
- Password security
- Data encryption
- Audit logging
- Secure file handling
- Error handling

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Web Security Cheat Sheet](https://cheatsheetseries.owasp.org/)
- [Python Security Guide](https://python-security.readthedocs.io/)
- [Cryptography Documentation](https://cryptography.io/en/latest/)

## Homework

1. Implement a secure authentication system:
   - Password hashing
   - Token management
   - Session security
   - 2FA support

2. Create a security audit tool:
   - Vulnerability scanning
   - Configuration checks
   - Dependency analysis
   - Security reporting

3. Build a secure API gateway:
   - Authentication
   - Rate limiting
   - Request validation
   - Response sanitization

## Next Steps

Tomorrow, we'll explore performance optimization in [Day 13: Performance Optimization](../day13/index.md). 