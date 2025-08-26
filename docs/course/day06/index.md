# 🚀 Day 6: Environment Configuration

## Using .env Files

Nexios supports environment configuration through `.env` files. First, install the `python-dotenv` package:

```bash
pip install python-dotenv
```

### Basic Configuration Setup

```python
from nexios import NexiosApp
from nexios.config import MakeConfig
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create configuration with environment variables
config = MakeConfig({
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "secret_key": os.getenv("SECRET_KEY", "default-secret-key"),
    "database_url": os.getenv("DATABASE_URL", "sqlite:///app.db"),
    "port": int(os.getenv("PORT", "8000")),
    "host": os.getenv("HOST", "127.0.0.1"),
    "cors": {
        "allow_origins": os.getenv("CORS_ORIGINS", "*").split(",")
    }
})

app = NexiosApp(config=config)
```

### Example .env File

Create a `.env` file in your project root:

```txt
# Application Settings
APP_NAME=My Nexios App
DEBUG=true
SECRET_KEY=your-super-secret-key-change-in-production
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# Server Configuration
HOST=127.0.0.1
PORT=8000
WORKERS=4

# CORS Settings
CORS_ORIGINS=http://localhost:3000,https://app.example.com

# Database Settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=postgres
DB_PASSWORD=password

# Security
ALLOWED_HOSTS=localhost,example.com
SESSION_SECRET=session-secret-key
```

### Environment-Specific Configuration

You can create different configurations for different environments:

```python
import os
from nexios import NexiosApp
from nexios.config import MakeConfig
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_development_config():
    """Development environment configuration"""
    return {
        "debug": True,
        "port": 8000,
        "host": "127.0.0.1",
        "secret_key": "dev-secret-key",
        "database_url": "sqlite:///dev.db",
        "cors": {
            "allow_origins": ["*"]
        }
    }

def get_production_config():
    """Production environment configuration"""
    return {
        "debug": False,
        "port": int(os.getenv("PORT", "8000")),
        "host": "0.0.0.0",
        "secret_key": os.getenv("SECRET_KEY"),
        "database_url": os.getenv("DATABASE_URL"),
        "cors": {
            "allow_origins": os.getenv("CORS_ORIGINS", "").split(",")
        }
    }

# Choose configuration based on environment
env = os.getenv("ENVIRONMENT", "development")
if env == "production":
    config = MakeConfig(get_production_config())
else:
    config = MakeConfig(get_development_config())

app = NexiosApp(config=config)
```

## CORS Configuration

Configure Cross-Origin Resource Sharing (CORS):

```python
from nexios import NexiosApp
from nexios.middleware import CORSMiddleware
from nexios.config import MakeConfig
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create configuration with CORS settings
config = MakeConfig({
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "cors": {
        "allow_origins": os.getenv("CORS_ORIGINS", "*").split(","),
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],
        "allow_credentials": True
    }
})

app = NexiosApp(config=config)

# Add CORS middleware
app.add_middleware(CORSMiddleware())
```

## Advanced Configuration Patterns

### Configuration with Validation

```python
import os
from nexios import NexiosApp
from nexios.config import MakeConfig
from dotenv import load_dotenv

load_dotenv()

def validate_config(config_dict):
    """Validate configuration values"""
    required_keys = ["SECRET_KEY", "DATABASE_URL"]
    missing_keys = [key for key in required_keys if not config_dict.get(key)]

    if missing_keys:
        raise ValueError(f"Missing required configuration: {missing_keys}")

    return config_dict

# Create configuration with validation
config_dict = {
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "secret_key": os.getenv("SECRET_KEY"),
    "database_url": os.getenv("DATABASE_URL"),
    "port": int(os.getenv("PORT", "8000")),
    "host": os.getenv("HOST", "127.0.0.1")
}

# Validate configuration
validated_config = validate_config(config_dict)
config = MakeConfig(validated_config)

app = NexiosApp(config=config)
```

### Configuration with Nested Settings

```python
import os
from nexios import NexiosApp
from nexios.config import MakeConfig
from dotenv import load_dotenv

load_dotenv()

config = MakeConfig({
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "server": {
        "host": os.getenv("HOST", "127.0.0.1"),
        "port": int(os.getenv("PORT", "8000")),
        "workers": int(os.getenv("WORKERS", "4"))
    },
    "database": {
        "url": os.getenv("DATABASE_URL"),
        "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "30"))
    },
    "security": {
        "secret_key": os.getenv("SECRET_KEY"),
        "session_timeout": int(os.getenv("SESSION_TIMEOUT", "3600")),
        "csrf_enabled": os.getenv("CSRF_ENABLED", "True").lower() == "true"
    },
    "cors": {
        "allow_origins": os.getenv("CORS_ORIGINS", "*").split(","),
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"]
    }
})

app = NexiosApp(config=config)

# Access nested configuration
print(f"Server host: {app.config.server.host}")
print(f"Database pool size: {app.config.database.pool_size}")
print(f"CSRF enabled: {app.config.security.csrf_enabled}")
```

## Best Practices

1. **Never commit `.env` files** - Add them to `.gitignore`
2. **Use different `.env` files** for different environments (`.env.development`, `.env.production`)
3. **Validate configuration** at startup to catch errors early
4. **Use strong secret keys** in production
5. **Document all environment variables** in your README
6. **Provide sensible defaults** for all configuration options
7. **Use type conversion** for numeric and boolean values
8. **Test configuration loading** in your test suite

## Example Project Structure

```
myapp/
├── .env                    # Environment variables
├── .env.example           # Example environment file
├── .gitignore             # Git ignore file
├── main.py                # Main application
├── config.py              # Configuration module
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

### .gitignore Entry

Make sure to add `.env` files to your `.gitignore`:

```txt
# Environment files
.env
.env.local
.env.development
.env.production
.env.test
```
