# Day 26: Deployment Strategies

## Learning Objectives
- Configure Nexios for production
- Implement deployment best practices
- Set up server environments
- Manage application lifecycle
- Handle deployment configurations


## Environment Management

Managing different environments:

```python
from nexios.config import get_config
import json
import os

# Load environment-specific configuration
def load_config():
    env = os.getenv("NEXIOS_ENV", "development")
    config_file = f"config/{env}.json"
    
    if os.path.exists(config_file):
        with open(config_file) as f:
            return json.load(f)
    
    return {
        "database_url": os.getenv("DATABASE_URL"),
        "redis_url": os.getenv("REDIS_URL"),
        "secret_key": os.getenv("SECRET_KEY"),
        "allowed_hosts": os.getenv("ALLOWED_HOSTS", "").split(","),
        "debug": env == "development"
    }

# Apply configuration
config = load_config()
app.config.update(config)
```

## Application Lifecycle

Managing application lifecycle:

```python
from nexios.websockets.channels import ChannelBox
import asyncio
import signal

# Startup handler
@app.on_startup
async def startup():
    # Initialize resources
    app.state.startup_time = asyncio.get_event_loop().time()
    
    # Start background tasks
    app.state.cleanup_task = asyncio.create_task(
        cleanup_channels()
    )

# Shutdown handler
@app.on_shutdown
async def shutdown():
    # Cancel background tasks
    if hasattr(app.state, "cleanup_task"):
        app.state.cleanup_task.cancel()
        try:
            await app.state.cleanup_task
        except asyncio.CancelledError:
            pass
    
    # Close all WebSocket connections
    await ChannelBox.close_all_connections()

# Channel cleanup task
async def cleanup_channels():
    while True:
        try:
            groups = await ChannelBox.show_groups()
            for group_name, channels in groups.items():
                for channel in channels:
                    if await channel._is_expired():
                        await ChannelBox.remove_channel_from_group(
                            channel,
                            group_name
                        )
            await asyncio.sleep(300)  # Run every 5 minutes
        except asyncio.CancelledError:
            break
```

## Health Checks

Implementing health checks:

```python
from nexios.http import Request, Response
import time

@app.get("/health")
async def health_check(request: Request, response: Response):
    # Basic health check
    uptime = time.time() - app.state.startup_time
    
    # Check WebSocket connections
    groups = await ChannelBox.show_groups()
    total_connections = sum(
        len(channels) for channels in groups.values()
    )
    
    return response.json({
        "status": "healthy",
        "uptime": uptime,
        "active_connections": total_connections,
        "version": "1.0.0"
    })

@app.get("/health/live")
async def liveness(request: Request, response: Response):
    """Kubernetes liveness probe"""
    return response.json({"status": "alive"})

@app.get("/health/ready")
async def readiness(request: Request, response: Response):
    """Kubernetes readiness probe"""
    # Check critical services
    services_ok = await check_services()
    
    if not services_ok:
        return Response(
            {"status": "not ready"},
            status_code=503
        )
    
    return response.json({"status": "ready"})
```

## Static Files

Serving static files in production:

```python
from nexios.static import StaticFilesHandler
import os

# Configure static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.add_route("/static", StaticFilesHandler(directory=static_dir))

@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=31536000"
    
    return response
```

## Logging Configuration

Production logging setup:

```python
from nexios.logging import create_logger
import logging.handlers
import sys

# Configure production logging
logger = create_logger(
    logger_name="production",
    log_level=logging.INFO,
    log_file="/var/log/nexios/app.log",
    max_bytes=10 * 1024 * 1024,  # 10MB
    backup_count=5
)

# Add JSON formatter for log aggregation
class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "process": record.process
        })

# Add JSON handler
json_handler = logging.StreamHandler(sys.stdout)
json_handler.setFormatter(JSONFormatter())
logger.addHandler(json_handler)
```

## Best Practices

1. Server Configuration:
   - Use environment variables
   - Configure appropriate worker count
   - Enable HTTP/2 in production
   - Set up proper logging

2. Application Lifecycle:
   - Handle startup/shutdown gracefully
   - Clean up resources properly
   - Manage background tasks
   - Implement health checks

3. Environment Management:
   - Use environment-specific configs
   - Secure sensitive data
   - Implement feature flags
   - Version control configurations

4. Monitoring:
   - Implement health checks
   - Set up logging
   - Monitor resources
   - Track metrics

## 📝 Practice Exercise

1. Create a production deployment:
   - Configure server settings
   - Set up environment management
   - Implement health checks
   - Configure logging

2. Implement deployment tools:
   - Deployment scripts
   - Configuration management
   - Health monitoring
   - Resource cleanup