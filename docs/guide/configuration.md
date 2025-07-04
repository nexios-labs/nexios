---
icon: gear-code
---

# Configuration Management

> **New in Nexios:** The CLI now supports a unified configuration system using a `nexios.config.py` file at your project root. This file is the default source for all CLI and server options. However, if `nexios.config.py` does not exist, you can pass configuration directly via CLI arguments, and these will take precedence. See the [CLI Guide](../guide/cli.md) for details.

## Configuration Fundamentals

Configuration in Nexios provides several key benefits:

- **Type Safety**: Strong typing for configuration values with automatic validation
- **Environment Variables**: Easy integration with environment variables for different deployment environments
- **Validation**: Built-in validation for configuration values to catch errors early
- **Immutability**: Configuration objects are immutable by default, preventing accidental changes
- **Nested Structure**: Support for complex configuration hierarchies for large applications
- **Default Values**: Sensible defaults with easy overrides for different environments
- **Security**: Secure handling of sensitive configuration data like API keys and passwords

## Configuration Best Practices

When managing configuration in your Nexios application, follow these best practices:

1. **Environment Separation**: Use different configurations for development, staging, and production environments
2. **Sensitive Data**: Never commit secrets, API keys, or passwords to version control
3. **Validation**: Validate configuration values at startup to catch configuration errors early
4. **Documentation**: Document all configuration options and their expected values
5. **Defaults**: Provide sensible defaults for all configuration options
6. **Type Safety**: Use type hints for configuration classes to catch errors at development time
7. **Testing**: Test configuration loading and validation in your test suite
8. **Monitoring**: Monitor configuration changes in production for debugging and audit purposes

## Security Considerations

Configuration security is critical for protecting your application and data:

- **Environment Variables**: Use environment variables for secrets and sensitive data
- **File Permissions**: Secure configuration files with proper file permissions
- **Encryption**: Encrypt sensitive configuration data when storing in databases or files
- **Rotation**: Regularly rotate secrets, API keys, and other sensitive configuration values
- **Access Control**: Limit access to configuration files and environment variables
- **Audit Logging**: Log configuration changes for audit trails and debugging

## Configuration Patterns

Different environments require different configuration patterns:

- **Development**: Debug mode enabled, local database connections, detailed logging, auto-reload
- **Staging**: Production-like settings, test data, monitoring enabled, limited debugging
- **Production**: Optimized settings, real data sources, minimal logging, security hardening
- **Testing**: Isolated settings, test databases, mock services, deterministic behavior

## Basic Usage

The most straightforward way to configure your Nexios application is by creating a `MakeConfig` instance and passing it to your application:

```python
from nexios import NexiosApp
from nexios.config import MakeConfig

config = MakeConfig({
    "port": 8000,
    "debug": True,
    "secret_key": "your-secret-key-here",
    "allowed_hosts": ["localhost", "127.0.0.1"]
})

app = NexiosApp(config=config)
```

You can access the configuration using the `config` attribute of the `NexiosApp` instance:

```python
from nexios import NexiosApp
from nexios.config import MakeConfig

config = MakeConfig({
    "port": 8000,
    "debug": True,
    "database_url": "postgresql://user:pass@localhost/dbname"
})

app = NexiosApp(config=config)

# Access configuration values
print(app.config.port)  # Output: 8000
print(app.config.debug)  # Output: True
print(app.config.database_url)  # Output: postgresql://user:pass@localhost/dbname

# Configuration is immutable by default
try:
    app.config.port = 9000  # This will raise an error
except AttributeError:
    print("Configuration is immutable")
```

## Global Configuration Access

The framework provides global configuration management through the `get_config()` function, allowing you to access configuration from anywhere in your application:

```python
from nexios.config import get_config, set_config
from nexios import NexiosApp

# Set up configuration
config = MakeConfig({
    "port": 8000,
    "debug": True,
    "database_url": "postgresql://user:pass@localhost/dbname"
})

app = NexiosApp(config=config)

# Access global configuration from startup handler
@app.on_startup()
async def startup_handler():
    config = get_config()
    print(f"Starting server on port {config.port}")
    print(f"Debug mode: {config.debug}")
    print(f"Database URL: {config.database_url}")

# Get global configuration from any handler
@app.get("/config")
async def get_config_handler(request, response):
    config = get_config()
    return response.json({
        "port": config.port,
        "debug": config.debug,
        "database_url": config.database_url
    })

# Access configuration from utility functions
def get_database_connection():
    config = get_config()
    return create_connection(config.database_url)
```

**Important**: You get access to the global configuration through the `get_config()` function from any module in your application. However, if you try to call `get_config()` before it has been set, it will raise a `RuntimeError`.

## Dynamic Configuration

You can set configuration dynamically using the `set_config()` function:

```python
from nexios import NexiosApp
from nexios.config import set_config, MakeConfig

# Create initial configuration
initial_config = MakeConfig({
    "port": 8000,
    "debug": True
})

app = NexiosApp(config=initial_config)

# Update configuration dynamically
@app.post("/update-config")
async def update_config(request, response):
    new_settings = await request.json
    
    # Create new configuration with updated values
    updated_config = MakeConfig({
        **initial_config.to_dict(),
        **new_settings
    })
    
    # Set the new configuration globally
    set_config(updated_config)
    
    return response.json({
        "message": "Configuration updated successfully",
        "new_config": updated_config.to_dict()
    })
```

## Environment-Based Configuration

### Using Environment Variables

Environment variables are the most common way to configure applications in different environments:

```python
import os
from nexios import NexiosApp, MakeConfig

# Load configuration from environment variables
config = MakeConfig({
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "secret_key": os.getenv("SECRET_KEY", "default-secret-key"),
    "database_url": os.getenv("DATABASE_URL", "sqlite:///app.db"),
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
    "port": int(os.getenv("PORT", "8000")),
    "host": os.getenv("HOST", "127.0.0.1"),
    "log_level": os.getenv("LOG_LEVEL", "INFO")
})

app = NexiosApp(config=config)
```

### Using .env Files

For development, you can use `.env` files to manage environment variables:

```python
from nexios import NexiosApp, MakeConfig
from nexios.config import load_env
import os

# Load environment variables from .env file
load_env()

config = MakeConfig({
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "secret_key": os.getenv("SECRET_KEY"),
    "database_url": os.getenv("DATABASE_URL"),
    "redis_url": os.getenv("REDIS_URL"),
    "port": int(os.getenv("PORT", "8000")),
    "host": os.getenv("HOST", "127.0.0.1")
})

app = NexiosApp(config=config)
```

Example `.env` file:
```ini
# Development Environment
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgresql://user:pass@localhost/dev_db
REDIS_URL=redis://localhost:6379
PORT=8000
HOST=127.0.0.1
LOG_LEVEL=DEBUG
```

### Environment-Specific Configuration

You can create different configuration classes for different environments:

```python
import os
from nexios import NexiosApp, MakeConfig

class BaseConfig:
    """Base configuration class with common settings"""
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "default-secret")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    def __init__(self):
        super().__init__()
        self.debug = True
        self.port = 8000
        self.host = "127.0.0.1"
        self.log_level = "DEBUG"
        self.reload = True

class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    def __init__(self):
        super().__init__()
        self.debug = False
        self.port = int(os.getenv("PORT", "8000"))
        self.host = "0.0.0.0"
        self.log_level = "WARNING"
        self.reload = False
        self.workers = int(os.getenv("WORKERS", "4"))

# Choose configuration based on environment
env = os.getenv("ENVIRONMENT", "development")
if env == "production":
    config = MakeConfig(ProductionConfig().__dict__)
else:
    config = MakeConfig(DevelopmentConfig().__dict__)

app = NexiosApp(config=config)
```

## Configuration Validation

Nexios provides built-in validation for configuration values:

```python
from nexios import NexiosApp, MakeConfig
from typing import List

# Configuration with validation
config = MakeConfig({
    "port": 8000,  # Must be an integer
    "debug": True,  # Must be a boolean
    "allowed_hosts": ["localhost", "127.0.0.1"],  # Must be a list of strings
    "database_url": "postgresql://user:pass@localhost/dbname",  # Must be a string
    "max_connections": 100,  # Must be a positive integer
    "timeout": 30.0  # Must be a positive float
})

# Custom validation function
def validate_config(config_dict):
    if config_dict["port"] < 1 or config_dict["port"] > 65535:
        raise ValueError("Port must be between 1 and 65535")
    
    if not config_dict["secret_key"] or len(config_dict["secret_key"]) < 32:
        raise ValueError("Secret key must be at least 32 characters long")
    
    if not config_dict["database_url"]:
        raise ValueError("Database URL is required")
    
    return config_dict

# Apply validation
validated_config = MakeConfig(validate_config({
    "port": 8000,
    "debug": True,
    "secret_key": "your-super-secret-key-that-is-long-enough",
    "database_url": "postgresql://user:pass@localhost/dbname"
}))

app = NexiosApp(config=validated_config)
```

## Advanced Configuration Patterns

### Nested Configuration

For complex applications, you can use nested configuration structures:

```python
from nexios import NexiosApp, MakeConfig

config = MakeConfig({
    "server": {
        "host": "127.0.0.1",
        "port": 8000,
        "workers": 4
    },
    "database": {
        "url": "postgresql://user:pass@localhost/dbname",
        "pool_size": 20,
        "max_overflow": 30,
        "timeout": 30
    },
    "redis": {
        "url": "redis://localhost:6379",
        "pool_size": 10,
        "timeout": 5
    },
    "security": {
        "secret_key": "your-secret-key",
        "session_timeout": 3600,
        "csrf_enabled": True
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "app.log"
    }
})

app = NexiosApp(config=config)

# Access nested configuration
print(app.config.server.host)  # 127.0.0.1
print(app.config.database.pool_size)  # 20
print(app.config.security.csrf_enabled)  # True
```

### Configuration Inheritance

You can create configuration inheritance patterns for different environments:

```python
import os
from nexios import NexiosApp, MakeConfig

def get_base_config():
    """Base configuration shared across all environments"""
    return {
        "secret_key": os.getenv("SECRET_KEY", "default-secret"),
        "database_url": os.getenv("DATABASE_URL", "sqlite:///app.db"),
        "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
        "log_level": os.getenv("LOG_LEVEL", "INFO")
    }

def get_development_config():
    """Development-specific configuration"""
    base_config = get_base_config()
    return {
        **base_config,
        "debug": True,
        "port": 8000,
        "host": "127.0.0.1",
        "reload": True,
        "database_url": "sqlite:///dev.db"
    }

def get_production_config():
    """Production-specific configuration"""
    base_config = get_base_config()
    return {
        **base_config,
        "debug": False,
        "port": int(os.getenv("PORT", "8000")),
        "host": "0.0.0.0",
        "reload": False,
        "workers": int(os.getenv("WORKERS", "4")),
        "log_level": "WARNING"
    }

def get_testing_config():
    """Testing-specific configuration"""
    base_config = get_base_config()
    return {
        **base_config,
        "debug": True,
        "port": 0,  # Use random port for testing
        "host": "127.0.0.1",
        "database_url": "sqlite:///test.db",
        "log_level": "DEBUG"
    }

# Choose configuration based on environment
env = os.getenv("ENVIRONMENT", "development")
config_functions = {
    "development": get_development_config,
    "production": get_production_config,
    "testing": get_testing_config
}

config = MakeConfig(config_functions[env]())
app = NexiosApp(config=config)
```

## Configuration Testing

Testing your configuration is important to catch configuration errors early:

```python
import pytest
from nexios.config import MakeConfig

def test_development_config():
    """Test development configuration"""
    config = MakeConfig({
        "debug": True,
        "port": 8000,
        "secret_key": "test-secret-key",
        "database_url": "sqlite:///test.db"
    })
    
    assert config.debug is True
    assert config.port == 8000
    assert config.secret_key == "test-secret-key"
    assert config.database_url == "sqlite:///test.db"

def test_production_config():
    """Test production configuration"""
    config = MakeConfig({
        "debug": False,
        "port": 8000,
        "secret_key": "production-secret-key",
        "database_url": "postgresql://user:pass@localhost/prod_db"
    })
    
    assert config.debug is False
    assert config.port == 8000
    assert len(config.secret_key) >= 32  # Ensure secret key is long enough

def test_config_validation():
    """Test configuration validation"""
    with pytest.raises(ValueError):
        # This should raise an error for invalid port
        config = MakeConfig({
            "port": 99999,  # Invalid port number
            "debug": True
        })

def test_environment_config():
    """Test environment-based configuration"""
    import os
    
    # Set environment variable
    os.environ["DEBUG"] = "true"
    os.environ["PORT"] = "9000"
    
    config = MakeConfig({
        "debug": os.getenv("DEBUG", "False").lower() == "true",
        "port": int(os.getenv("PORT", "8000"))
    })
    
    assert config.debug is True
    assert config.port == 9000
```

## Configuration Monitoring

Monitoring configuration changes can help with debugging and auditing:

```python
import logging
from nexios import NexiosApp, MakeConfig
from nexios.config import set_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_config_change(old_config, new_config):
    """Log configuration changes for monitoring"""
    logger.info("Configuration changed")
    logger.info(f"Old config: {old_config.to_dict()}")
    logger.info(f"New config: {new_config.to_dict()}")

# Create initial configuration
initial_config = MakeConfig({
    "debug": True,
    "port": 8000,
    "secret_key": "initial-secret"
})

app = NexiosApp(config=initial_config)

@app.post("/update-config")
async def update_config(request, response):
    new_settings = await request.json
    
    # Get current configuration
    current_config = get_config()
    
    # Create new configuration
    updated_config = MakeConfig({
        **current_config.to_dict(),
        **new_settings
    })
    
    # Log the change
    log_config_change(current_config, updated_config)
    
    # Set the new configuration
    set_config(updated_config)
    
    return response.json({
        "message": "Configuration updated successfully"
    })
```

## CLI-Driven and Application-Wide Configuration: `nexios.config.py` and CLI Args

::: tip nexios.config.py: CLI & App-Wide Config
If a `nexios.config.py` file is present at your project root, its values will be **automatically loaded** for both the CLI and as application-wide configuration. This means you can use it to define settings for your app, your server, and any custom project variables. If the file is missing, you can provide all necessary options via CLI arguments (e.g., `nexios run --app-path main:app --port 8080`). CLI arguments always take precedence over config file values.
:::

- **nexios.config.py**: Place this file at your project root to define all your app/server options as plain Python variables (e.g., `app_path`, `server`, `port`, etc.), as well as any custom configuration your application needs. The CLI and your app can both import and use these settings.
- **Bypassing the Config File**: If `nexios.config.py` is missing, you can provide all necessary options via CLI arguments. CLI arguments always take precedence over config file values.
- **Best Practice**: For consistency and portability, keep a `nexios.config.py` in version control. Use CLI args for quick overrides or in CI/CD pipelines.
- **Migration**: If you used the old config system, simply move your options to `nexios.config.py` as plain variables. The CLI and your app will handle the rest.

For more, see the [Nexios CLI & Configuration Guide](../guide/cli.md).

This comprehensive configuration guide covers all aspects of managing configuration in Nexios applications. The configuration system is designed to be flexible, secure, and easy to use while providing the power to handle complex configuration scenarios across different environments.

