# Day 11: Request Validation with Pydantic

## Input Validation Basics

Implementing basic input validation:

```python
from nexios import NexiosApp
from typing import Optional, List
from pydantic import BaseModel, EmailStr,ValidationError

app = NexiosApp()

# Basic field validation
class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9_-]+$"
    )
    email: EmailStr
    password: str = Field(min_length=8)
    age: Optional[int] = Field(ge=0, lt=150)
    interests: List[str] = Field(max_items=10)

@app.post("/users")
async def create_user(request: Request, response: Response):
    request_data = await request.json
    try:
      data =  UserCreate(**request_data)
    except as err:
      return response.json(err.data)

    return {
        "username": data.username,
        "email": data.email,
        "age": data.age,
        "interests": data.interests
    }

```

## Custom Validators

Creating custom validation logic:

```python
from nexios.validation import validator
from typing import Any

class PasswordValidator(BaseModel):
    password: str

    @validator("password")
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password too short")

        if not any(c.isupper() for c in v):
            raise ValueError(
                "Password must contain uppercase letter"
            )

        if not any(c.islower() for c in v):
            raise ValueError(
                "Password must contain lowercase letter"
            )

        if not any(c.isdigit() for c in v):
            raise ValueError(
                "Password must contain number"
            )

        return v

class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, v: str, values: dict[str, Any]) -> str:
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

    @validator("password")
    def strong_password(cls, v: str) -> str:
        PasswordValidator(password=v)
        return v

@app.post("/register")
async def register(data: UserRegistration):
    # All validation passed
    return {"message": "Registration successful"}

# Custom field validator
def validate_phone(v: str) -> str:
    if not v.startswith("+"):
        raise ValueError("Phone must start with +")

    digits = v[1:]
    if not digits.isdigit():
        raise ValueError("Invalid phone number")

    if not 10 <= len(digits) <= 15:
        raise ValueError("Invalid phone length")

    return v

class Contact(BaseModel):
    name: str
    phone: str

    _validate_phone = validator("phone", allow_reuse=True)(
        validate_phone
    )
```

## Error Handling

Handling validation errors:

```python
from typing import Any
from pydantic imprt ValidationError
from nexios.http import Request, Response
@app.add_exception_handler(ValidationError)
async def validation_error_handler(
    request: Request,
    response:Response,
    exc: ValidationError
) :
    errors = []

    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return response.json(
        content={
            "detail": "Validation error",
            "errors": errors
        }
        status_code=422,
    )

# Custom error messages
class Item(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=50,
        description="Item name",
        error_messages={
            "min_length": "Name too short",
            "max_length": "Name too long"
        }
    )
    price: Decimal = Field(
        ge=0,
        description="Item price",
        error_messages={
            "ge": "Price must be positive"
        }
    )

# Conditional validation
class Discount(BaseModel):
    type: str  # "percentage" or "fixed"
    value: Decimal

    @validator("value")
    def validate_discount(cls, v: Decimal, values: dict[str, Any]) -> Decimal:
        if "type" not in values:
            raise ValueError("Discount type required")

        if values["type"] == "percentage":
            if not 0 <= v <= 100:
                raise ValueError(
                    "Percentage must be between 0 and 100"
                )
        else:  # fixed
            if v < 0:
                raise ValueError(
                    "Fixed discount must be positive"
                )

        return v
```

## 📝 Practice Exercise

1. Create a validation system for:

   - User registration
   - Product creation
   - Order processing
   - Payment validation

2. Implement custom validators for:

   - Complex passwords
   - Phone numbers
   - Credit cards
   - Date ranges

3. Build error handling for:
   - Field validation
   - Business rules
   - Custom error messages
   - Error logging

## 📚 Additional Resources

- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Error Handling](../../guide/error-handling.md)

## 🎯 Next Steps

Tomorrow in [Day 12: File Uploads](../day12/index.md), we'll explore:

- File upload handling
- Multipart form data
- File validation
- Storage options

# Day 11: Deployment

Welcome to Day 11! Today we'll learn how to deploy Nexios applications to production environments.

## Understanding Deployment

Key aspects of deployment:

- Server configuration
- Environment management
- Process management
- Load balancing
- Monitoring
- Security
- Continuous deployment

## Basic Deployment Setup

### 1. Project Structure

```
myapp/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── routes/
│   └── services/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── gunicorn.conf.py
└── README.md
```

### 2. Configuration Management

```python
# app/config.py
from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    app_name: str = "Nexios App"
    debug: bool = False
    database_url: str
    redis_url: str = "redis://localhost"
    secret_key: str
    allowed_hosts: list = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. ASGI Server Setup

```python
# gunicorn.conf.py
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = "nexios_app"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# SSL
keyfile = "ssl/private.key"
certfile = "ssl/cert.pem"
```

## Docker Deployment

### 1. Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/app
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=your-secret-key
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    restart: always

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Nginx Configuration

```nginx
# /etc/nginx/sites-available/nexios_app
upstream nexios_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://nexios_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static/ {
        alias /path/to/your/static/files/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        alias /path/to/your/media/files/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

## Systemd Service

```ini
# /etc/systemd/system/nexios_app.service
[Unit]
Description=Nexios Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/venv/bin"
Environment="DATABASE_URL=postgresql://user:password@localhost:5432/app"
Environment="REDIS_URL=redis://localhost:6379"
Environment="SECRET_KEY=your-secret-key"
ExecStart=/path/to/your/venv/bin/gunicorn app.main:app -c gunicorn.conf.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Deployment Scripts

### 1. Database Migration Script

```python
# scripts/migrate.py
import asyncio
from app.models import metadata
from app.config import settings
from sqlalchemy import create_engine

async def migrate():
    engine = create_engine(settings.database_url)
    metadata.create_all(engine)
    print("Database migration completed")

if __name__ == "__main__":
    asyncio.run(migrate())
```

### 2. Deployment Script

```bash
#!/bin/bash
# scripts/deploy.sh

# Pull latest changes
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
python scripts/migrate.py

# Restart services
sudo systemctl restart nexios_app
sudo systemctl restart nginx

# Check status
sudo systemctl status nexios_app
sudo systemctl status nginx
```

## Monitoring Setup

### 1. Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "nexios_app"
    static_configs:
      - targets: ["localhost:8000"]
```

### 2. Application Metrics

```python
from prometheus_client import Counter, Histogram
import time

# Metrics
REQUEST_COUNT = Counter(
    'nexios_request_count',
    'Number of requests received'
)

REQUEST_LATENCY = Histogram(
    'nexios_request_latency_seconds',
    'Request latency in seconds'
)

# Middleware
async def metrics_middleware(request: Request, response: Response, call_next):
    REQUEST_COUNT.inc()

    start_time = time.time()
    response = await call_next()
    duration = time.time() - start_time

    REQUEST_LATENCY.observe(duration)
    return response

app.add_middleware(metrics_middleware)
```

## Load Balancing

### 1. HAProxy Configuration

```txt
# /etc/haproxy/haproxy.cfg
global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 5000
    timeout client  50000
    timeout server  50000

frontend http_front
    bind *:80
    stats uri /haproxy?stats
    default_backend http_back

backend http_back
    balance roundrobin
    server web1 127.0.0.1:8001 check
    server web2 127.0.0.1:8002 check
    server web3 127.0.0.1:8003 check
```

## Continuous Deployment

### 1. GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.9"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest

      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /path/to/app
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            python scripts/migrate.py
            sudo systemctl restart nexios_app
```

## Mini-Project: Complete Deployment Setup

Create a complete deployment setup for a Nexios application:

1. Application Structure:

```
myapp/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── api.py
│   └── services/
│       ├── __init__.py
│       └── database.py
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   └── test_api.py
├── scripts/
│   ├── migrate.py
│   └── deploy.sh
├── deployment/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── prometheus.yml
├── requirements.txt
├── gunicorn.conf.py
└── README.md
```

2. Main Application:

```python
# app/main.py
from nexios import NexiosApp
from app.config import settings
from app.routes import auth, api
import prometheus_client
from prometheus_client import Counter, Histogram
import time

app = NexiosApp()

# Add routes
app.include_router(auth.router)
app.include_router(api.router)

# Metrics
REQUEST_COUNT = Counter(
    'nexios_request_count',
    'Number of requests received'
)

REQUEST_LATENCY = Histogram(
    'nexios_request_latency_seconds',
    'Request latency in seconds'
)

# Middleware
@app.middleware("http")
async def metrics_middleware(request, response, call_next):
    REQUEST_COUNT.inc()

    start_time = time.time()
    response = await call_next()
    duration = time.time() - start_time

    REQUEST_LATENCY.observe(duration)
    return response

# Metrics endpoint
@app.get("/metrics")
async def metrics(request, response):
    return response.text(prometheus_client.generate_latest())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
```

3. Deployment Script:

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

# Configuration
APP_DIR="/path/to/app"
VENV_DIR="$APP_DIR/venv"
BRANCH="main"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting deployment...${NC}"

# Navigate to app directory
cd $APP_DIR

# Update code
echo -e "${GREEN}Pulling latest changes...${NC}"
git fetch origin $BRANCH
git reset --hard origin/$BRANCH

# Update dependencies
echo -e "${GREEN}Updating dependencies...${NC}"
source $VENV_DIR/bin/activate
pip install -r requirements.txt

# Run migrations
echo -e "${GREEN}Running database migrations...${NC}"
python scripts/migrate.py

# Collect static files
echo -e "${GREEN}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Restart services
echo -e "${GREEN}Restarting services...${NC}"
sudo systemctl restart nexios_app
sudo systemctl restart nginx

# Check service status
echo -e "${GREEN}Checking service status...${NC}"
sudo systemctl status nexios_app --no-pager
sudo systemctl status nginx --no-pager

echo -e "${GREEN}Deployment completed successfully!${NC}"
```

## Key Concepts Learned

- Server configuration
- Docker containerization
- Load balancing
- Reverse proxy setup
- Process management
- Monitoring and metrics
- Continuous deployment
- SSL/TLS configuration
- Environment management

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [GitHub Actions](https://docs.github.com/en/actions)

## Homework

1. Create a complete deployment pipeline:

   - Automated testing
   - Docker builds
   - Database migrations
   - Zero-downtime deployment

2. Set up monitoring:

   - Application metrics
   - System metrics
   - Log aggregation
   - Alerting

3. Implement scaling:
   - Load balancing
   - Auto-scaling
   - Database replication
   - Cache distribution

## Next Steps

Tomorrow, we'll explore security best practices in [Day 12: Security](../day12/index.md).
