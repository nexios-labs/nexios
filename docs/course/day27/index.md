# Day 27: Docker & Containers

## Learning Objectives
- Containerize Nexios applications
- Configure Docker for development and production
- Manage container lifecycle
- Implement container best practices

## Basic Dockerfile

Creating a Dockerfile for Nexios:

```dockerfile
# Use Python 3.8 or later
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV NEXIOS_ENV=production
ENV HOST=0.0.0.0
ENV PORT=8000

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "-m", "nexios", "run", "--host", "0.0.0.0", "--port", "8000"]
```

## Development Setup

Docker Compose for development:

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: 
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - NEXIOS_ENV=development
      - DEBUG=1
      - HOST=0.0.0.0
      - PORT=8000
    command: python -m nexios run --reload

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

Development Dockerfile:

```dockerfile
# Dockerfile.dev
FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Don't copy code - will be mounted as volume
```

## Production Setup

Production Docker Compose:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    build: 
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - NEXIOS_ENV=production
      - HOST=0.0.0.0
      - PORT=8000
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

## Application Configuration

Adapting Nexios for containerization:

```python
from nexios import NexiosApp
from nexios.config import MakeConfig
import os

# Server configuration
server_config = MakeConfig({
    "host": os.getenv("HOST", "0.0.0.0"),
    "port": int(os.getenv("PORT", "8000")),
    "workers": int(os.getenv("WORKERS", "1")),
    "interface": "asgi",
    "http_protocol": "h2",
    "log_level": os.getenv("LOG_LEVEL", "info"),
    "threading": True,
    "access_log": True,
    "server": "uvicorn"
})

app = NexiosApp(config=server_config)

# Health check for container orchestration
@app.get("/health")
async def health_check(request, response):
    return response.json({
        "status": "healthy",
        "container_id": os.getenv("HOSTNAME", "unknown")
    })
```

## Container Lifecycle

Managing container lifecycle:

```python
from nexios.websockets.channels import ChannelBox
import signal
import sys

# Graceful shutdown handler
def handle_sigterm(signum, frame):
    print("Received SIGTERM. Performing graceful shutdown...")
    # Close WebSocket connections
    asyncio.run(ChannelBox.close_all_connections())
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)

# Startup handler
@app.on_startup
async def startup():
    print(f"Container {os.getenv('HOSTNAME')} starting up...")
    # Initialize container-specific resources
    app.state.container_id = os.getenv("HOSTNAME")

# Shutdown handler
@app.on_shutdown
async def shutdown():
    print(f"Container {app.state.container_id} shutting down...")
    # Cleanup container-specific resources
    await ChannelBox.close_all_connections()
```

## Logging Configuration

Container-friendly logging:

```python
from nexios.logging import create_logger
import sys
import json

# Configure logging for containers
logger = create_logger(
    logger_name="container",
    log_level="info"
)

# JSON formatter for container logs
class ContainerLogFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "container_id": os.getenv("HOSTNAME", "unknown"),
            "service": "nexios"
        })

# Configure container logging
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(ContainerLogFormatter())
logger.addHandler(handler)
```

## Multi-stage Build

Optimized production Dockerfile:

```dockerfile
# Build stage
FROM python:3.8-slim as builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.8-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY . .

ENV NEXIOS_ENV=production
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000
CMD ["python", "-m", "nexios", "run"]
```

## Best Practices

1. Container Configuration:
   - Use environment variables
   - Implement health checks
   - Handle signals properly
   - Configure logging

2. Development Workflow:
   - Use volumes for code mounting
   - Enable hot reload
   - Share development services
   - Use development-specific settings

3. Production Deployment:
   - Use multi-stage builds
   - Implement proper scaling
   - Configure health checks
   - Set up monitoring

4. Security:
   - Use non-root users
   - Scan for vulnerabilities
   - Minimize container size
   - Secure sensitive data

## 📝 Practice Exercise

1. Create Docker configurations:
   - Development environment
   - Production environment
   - Multi-container setup
   - Health monitoring

2. Implement container features:
   - Graceful shutdown
   - Log aggregation
   - Resource monitoring
   - Container orchestration 