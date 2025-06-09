---
icon: gear-code
---

# Managing Config

The Nexios framework provides a flexible and dynamic configuration system through its `MakeConfig` class. This system allows for structured configuration management with support for nested attributes, validation, and immutability.

## Basic Usage

```python
from nexios import NexiosApp
from nexios.config import MakeConfig

config = MakeConfig({
    "port": 8000,
    "debug": True
})

app = NexiosApp(config = config)

```

You can access the configuration using the `config` attribute of the `NexiosApp` instance:

```python
from nexios import NexiosApp
from nexios.config import MakeConfig

config = MakeConfig({
    "port": 8000,
    "debug": True
})

app = NexiosApp(config = config)

print(app.config.port)  # Output: 8000
print(app.config.debug)  # Output: True

```

##  Accessing Configuration Globally

The framework provides global configuration management through:

```python
from nexios.config import get_config
from nexios import NexiosApp

app = NexiosApp()
# Access global configuration from startup handler
@app.on_startup
async def startup_handler():
    config = get_config()
    print(config.port)  # Output: 8000
# Get global configuration from handler
@app.get("/config")
async def get_config_handler(req, res):
    config = get_config()
    print(config.port)  # Output: 8000
    print(config.debug)  # Output: True
    ...
```

::: tip 💡Tip
You get access to the global configuration through the `get_config` function from any module in your application.
:::

::: warning ⚠️ Warning
If you try `get_config` before it has been set, it will raise an exception.
:::

## Set Config Dynamically

```python
from nexios import NexiosApp
from nexios.config import set_config

config = MakeConfig({
    "port": 8000,
    "debug": True
})

app = NexiosApp()
set_config(config)

```

# Configuration

Nexios provides a flexible configuration system that allows you to customize your application's behavior through various settings and options.

## Basic Configuration

### Configuration Options

::: code-group
```python [Basic Config]
from nexios import NexiosApp, MakeConfig

config = MakeConfig(
    debug=True,
    secret_key="your-secret-key",
    allowed_hosts=["localhost", "127.0.0.1"]
)

app = NexiosApp(config=config)
```

```python [Environment Variables]
from nexios import NexiosApp, MakeConfig
from nexios.config import load_env

# Load .env file
load_env()

config = MakeConfig(
    debug="${DEBUG:bool}",
    secret_key="${SECRET_KEY}",
    database_url="${DATABASE_URL}",
    redis_url="${REDIS_URL}"
)

app = NexiosApp(config=config)
```

```python [JSON Config]
from nexios import NexiosApp, MakeConfig
import json

with open("config.json") as f:
    config_data = json.load(f)

config = MakeConfig(**config_data)
app = NexiosApp(config=config)
```
:::

### Available Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `debug` | bool | `False` | Enable debug mode |
| `secret_key` | str | Required | Secret key for security |
| `allowed_hosts` | List[str] | `["*"]` | Allowed host/domain names |
| `cors_enabled` | bool | `False` | Enable CORS middleware |
| `cors_origins` | List[str] | `["*"]` | Allowed CORS origins |
| `database_url` | str | None | Database connection URL |
| `redis_url` | str | None | Redis connection URL |
| `static_dir` | str | "static" | Static files directory |
| `template_dir` | str | "templates" | Template files directory |
| `log_level` | str | "INFO" | Logging level |
| `workers` | int | 1 | Number of worker processes |
| `reload` | bool | `False` | Enable auto-reload |
| `port` | int | 8000 | Server port |
| `host` | str | "127.0.0.1" | Server host |

## Environment Configuration

### Using .env Files

```ini
# .env
DEBUG=true
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost
ALLOWED_HOSTS=localhost,example.com
CORS_ORIGINS=http://localhost:3000,https://example.com
LOG_LEVEL=DEBUG
```

### Loading Environment Variables

```python
from nexios import NexiosApp, MakeConfig
from nexios.config import load_env

# Load .env file
load_env()

# Load specific file
load_env(".env.production")

# Load with override
load_env(override=True)

config = MakeConfig(
    debug="${DEBUG:bool}",
    secret_key="${SECRET_KEY}",
    database_url="${DATABASE_URL}",
    redis_url="${REDIS_URL}",
    allowed_hosts="${ALLOWED_HOSTS:list}",
    cors_origins="${CORS_ORIGINS:list}",
    log_level="${LOG_LEVEL}"
)

app = NexiosApp(config=config)
```

## Advanced Configuration






### CORS Settings

```python
config = MakeConfig(
    cors = {}
)
```

### Security Headers

```python
config = MakeConfig(
    security_headers={
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    },
    csp_enabled=True,
    csp_policy={
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:", "https:"],
        "connect-src": ["'self'", "https://api.example.com"]
    }
)
```

## Database Configuration

### SQLAlchemy Settings

```python
config = MakeConfig(
    database_url="postgresql+asyncpg://user:pass@localhost/db",
    database_pool_size=20,
    database_max_overflow=10,
    database_pool_timeout=30,
    database_echo=False,
    database_ssl=True,
    database_ssl_verify=True
)
```

### MongoDB Settings

```python
config = MakeConfig(
    mongodb_url="mongodb://localhost",
    mongodb_database="app",
    mongodb_min_pool_size=10,
    mongodb_max_pool_size=100,
    mongodb_timeout_ms=5000
)
```

## Logging Configuration

### Basic Logging

```python
config = MakeConfig(
    log_level="DEBUG",
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file="app.log",
    log_rotation="1 day",
    log_retention="30 days",
    log_compression="gz"
)
```

### Advanced Logging

```python
import logging.config

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "formatter": "json",
            "maxBytes": 10485760,
            "backupCount": 5
        }
    },
    "loggers": {
        "nexios": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

config = MakeConfig(logging_config=logging_config)
```

