The Nexios framework provides a flexible and dynamic configuration system through its `MakeConfig` class. This system allows for structured configuration management with support for nested attributes, validation, and immutability.

## Core Configuration Components

### `MakeConfig` Class

The main configuration class that provides:

- Dictionary-like configuration with attribute access
- Nested configuration support
- Validation rules
- Immutability option
- Conversion to dict/JSON

```python
class MakeConfig:
    def __init__(
        self,
        config: Dict[str, Any],
        defaults: Optional[Dict[str, Any]] = None,
        validate: Optional[Dict[str, Callable[[Any], bool]]] = None,
        immutable: bool = False,
    ):
        ...
```

### Key Features

1. **Attribute Access**:

   ```python
   config = MakeConfig({"db": {"host": "localhost"}})
   print(config.db.host)  # "localhost"
   ```

2. **Dictionary Access**:

   ```python
   print(config["db.host"])  # "localhost"
   ```

3. **Validation**:

   ```python
   validate_rules = {"port": lambda x: x > 0}
   config = MakeConfig({"port": 8080}, validate=validate_rules)
   ```

4. **Immutability**:

   ```python
   config = MakeConfig({"debug": True}, immutable=True)
   config.debug = False  # Raises AttributeError
   ```

5. **Conversion**:
   ```python
   config.to_dict()  # Convert to regular dictionary
   config.to_json()  # Convert to JSON string
   ```

## Global Configuration Management

The framework provides global configuration management through:

```python
from nexios.config import set_config, get_config, DEFAULT_CONFIG

# Set global configuration
config = MakeConfig({"debug": True})
set_config(config)

# Get global configuration
current_config = get_config()
```

### Default Configuration

A default configuration is provided:

```python
DEFAULT_CONFIG = MakeConfig({"debug": True})
```

## Application Configuration

When creating a Nexios application, you can pass your configuration:

```python
from nexios import get_application

config = MakeConfig({
    "debug": True,
    "database": {
        "host": "localhost",
        "port": 5432
    }
})

app = get_application(config=config)
```

## Configuration Structure

The configuration system supports nested structures:

```python
config = MakeConfig({
    "app": {
        "name": "MyApp",
        "version": "1.0.0"
    },
    "database": {
        "host": "db.example.com",
        "credentials": {
            "username": "admin",
            "password": "secret"
        }
    }
})
```

## Best Practices

1. **Validation**: Define validation rules for critical configuration values

   ```python
   validate_rules = {
       "port": lambda x: isinstance(x, int) and 1024 <= x <= 65535,
       "debug": lambda x: isinstance(x, bool)
   }
   ```

2. **Immutability**: Consider making configurations immutable in production

   ```python
   config = MakeConfig(production_config, immutable=True)
   ```

3. **Defaults**: Use defaults for optional configuration values

   ```python
   defaults = {"debug": False, "port": 8000}
   config = MakeConfig(user_config, defaults=defaults)
   ```

4. **Environment Separation**: Maintain separate configurations for different environments (dev, staging, prod)

## Accessing Configuration in Application

Once set, the configuration can be accessed anywhere in your application:

```python
from nexios.config import get_config

config = get_config()
if config.debug:
    print("Debug mode is enabled")
```

## Error Handling

The system provides clear error messages:

- When accessing uninitialized configuration:
  ```python
  RuntimeError: Configuration has not been initialized.
  ```
- When validation fails:
  ```python
  ValueError: Invalid value for 'port': -1
  ```
- When modifying immutable config:
  ```python
  AttributeError: Cannot modify immutable config: 'debug'
  ```

This configuration system provides a robust way to manage application settings while maintaining flexibility and type safety.
