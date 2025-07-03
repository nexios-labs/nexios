import json
import multiprocessing
import os
from typing import (
    Any,
    Callable,
    Dict,
    Literal,
    Optional,
    TypedDict,
    TypeVar,
    cast,
)

# Type definitions for server configuration
InterfaceType = Literal["asgi", "wsgi", "asgi-http"]
HttpProtocolType = Literal["h11", "h2", "auto"]
LogLevelType = Literal["critical", "error", "warning", "info", "debug", "trace"]
ServerType = Literal["auto", "uvicorn", "granian"]


class ServerConfigDict(TypedDict, total=False):
    """TypedDict for server configuration options."""

    host: str
    port: int
    workers: int
    interface: InterfaceType
    http_protocol: HttpProtocolType
    log_level: LogLevelType
    reload: bool
    threading: bool
    access_log: bool
    server: ServerType


# Type for configuration validation functions
T = TypeVar("T")
ValidationFunc = Callable[[T], bool]


class MakeConfig:
    """
    A dynamic configuration class that allows nested dictionary access as attributes,
    with optional validation and immutability.

    Attributes:
        _config (dict): Stores configuration data.
        _immutable (bool): If True, prevents modifications.
        _validate (dict): Stores validation rules for keys.

    Example Usage:
        config = MakeConfig({"db": {"host": "localhost"}}, immutable=True)
        print(config.db.host)  # "localhost"
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        *,
        defaults: Optional[Dict[str, Any]] = None,
        validate: Optional[Dict[str, Callable[[Any], bool]]] = None,
        immutable: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize the configuration object.

        Args:
            config (dict): Initial configuration.
            defaults (dict, optional): Default values for missing keys.
            validate (dict, optional): Validation rules (e.g., {"port": lambda x: x > 0}).
            immutable (bool, optional): If True, prevents modifications.
        """
        self._config: Dict[str, Any] = {}
        self._immutable: bool = immutable
        self._validate: Dict[str, Callable[[Any], bool]] = validate or {}

        config = config or {}
        # Merge defaults, config dict, and kwargs, kwargs take highest priority
        merged_config = {**(defaults or {}), **config, **kwargs}

        for key, value in merged_config.items():
            self._set_config(key, value)

    def _set_config(self, key: str, value: Optional[Any]):
        """Validates and sets a configuration key."""
        if key in self._validate:
            if not self._validate[key](value):
                raise ValueError(f"Invalid value for '{key}': {value}")
        if isinstance(value, dict):
            value = MakeConfig(value, immutable=self._immutable)  # type: ignore
        self._config[key] = value

    def __setattr__(self, name: str, value: Any):
        """Handles attribute assignment while respecting immutability."""
        if name in {"_config", "_immutable", "_validate"}:
            super().__setattr__(name, value)
        elif self._immutable:
            raise AttributeError(f"Cannot modify immutable config: '{name}'")
        else:
            self._set_config(name, value)

    def __getattr__(self, name: str) -> Any:
        """Handles attribute access, returning None if key is missing."""
        return self._config.get(name, None)

    def _get_nested(self, path: str) -> Any:
        """
        Retrieve a value from nested keys, returning None if any part is missing.

        Args:
            path (str): Dot-separated path, e.g., "db.host".

        Returns:
            Any: The value found or None.
        """
        keys = path.split(".")
        current: Any = self
        for key in keys:
            if not isinstance(current, MakeConfig):
                return None
            current = current._config.get(key, None)
        return current

    def __getitem__(self, path: str) -> Any:
        """Allow dictionary-like access via dot-separated keys."""
        return self._get_nested(path)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a standard dictionary."""

        def recurse(config: "MakeConfig") -> Dict[str, Any]:
            if isinstance(config, MakeConfig):  # type: ignore
                return {k: recurse(v) for k, v in config._config.items()}
            return config

        return recurse(self)

    def to_json(self) -> str:
        """Convert configuration to a JSON string."""
        return json.dumps(self.to_dict(), indent=4)

    def __repr__(self) -> str:
        return f"MakeConfig({self.to_dict()})"

    def __str__(self) -> str:
        return self.to_json()

    def update(self, data: Dict[str, Any], *, recursive: bool = True) -> None:
        """
        Update the configuration with values from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary of values to update.
            recursive (bool): If True, update nested MakeConfig objects recursively.
        """
        for key, value in data.items():
            if (
                recursive
                and key in self._config
                and isinstance(self._config[key], MakeConfig)
                and isinstance(value, dict)
            ):
                self._config[key].update(value, recursive=True)
            else:
                self._set_config(key, value)


# Server configuration validation
SERVER_VALIDATION: Dict[str, ValidationFunc[Any]] = {
    # Host validation: must be a string
    "host": lambda x: isinstance(x, str),
    # Port validation: must be an integer between 1 and 65535
    "port": lambda x: isinstance(x, int) and 1 <= x <= 65535,
    # Workers validation: must be a positive integer
    "workers": lambda x: isinstance(x, int) and x > 0,
    # Interface validation: must be one of the supported interface types
    "interface": lambda x: isinstance(x, str) and x in ["asgi", "wsgi", "asgi-http"],
    # HTTP protocol validation: must be one of the supported protocols
    "http_protocol": lambda x: isinstance(x, str) and x in ["h11", "h2", "auto"],
    # Log level validation: must be one of the supported log levels
    "log_level": lambda x: isinstance(x, str)
    and x in ["critical", "error", "warning", "info", "debug", "trace"],
    # Reload validation: must be a boolean
    "reload": lambda x: isinstance(x, bool),
    # Threading validation: must be a boolean
    "threading": lambda x: isinstance(x, bool),
    # Access log validation: must be a boolean
    "access_log": lambda x: isinstance(x, bool),
    # Server validation: must be one of the supported server types
    "server": lambda x: isinstance(x, str) and x in ["auto", "uvicorn", "granian"],
}


# Function to safely get environment variables with type conversion
def _get_env_int(key: str, default: int) -> int:
    """Get an integer environment variable with a default value."""
    try:
        value = os.environ.get(key)
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def _get_env_bool(key: str, default: bool) -> bool:
    """Get a boolean environment variable with a default value."""
    value = os.environ.get(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "t", "yes", "y")


"""
Default server configuration for Nexios applications.
This configuration is used when running the application with 'nexios run'.
Environment variables can override these defaults:

HOST:           The host to bind the server to (default: 127.0.0.1)
PORT:           The port to bind the server to (default: 4000)
WORKERS:        Number of worker processes (default: min(CPU count + 1, 8))
INTERFACE:      Server interface type: asgi, wsgi, or asgi-http (default: asgi)
HTTP_PROTOCOL:  HTTP protocol: h11, h2, or auto (default: auto)
LOG_LEVEL:      Logging level (default: info)
RELOAD:         Enable auto-reload on code changes (default: true)
THREADING:      Enable threading (default: false)
ACCESS_LOG:     Enable access logging (default: true)
SERVER:         Server to use: auto, uvicorn, or granian (default: auto)

Example usage in code:

```python
from nexios.config import get_config

config = get_config()
server_config = config.server

# Access server settings
host = server_config.host  # "127.0.0.1"
port = server_config.port  # 4000
```

Or override in your application:

```python
from nexios.config import MakeConfig, DEFAULT_SERVER_CONFIG

# Create custom server config
my_server_config = {
    **DEFAULT_SERVER_CONFIG,
    "port": 8000,
    "workers": 4
}

# Create application config
app_config = MakeConfig({
    "debug": True,
    "server": my_server_config
})
```
"""
DEFAULT_SERVER_CONFIG: ServerConfigDict = {
    # The host to bind the server to
    "host": os.environ.get("HOST", "127.0.0.1"),
    # The port to bind the server to
    "port": _get_env_int("PORT", 4000),
    # Number of worker processes to use
    "workers": _get_env_int("WORKERS", min(multiprocessing.cpu_count() + 1, 8)),
    # The interface to use (asgi, wsgi, or asgi-http)
    "interface": cast(InterfaceType, os.environ.get("INTERFACE", "asgi")),
    # The HTTP protocol to use (h11, h2, or auto)
    "http_protocol": cast(HttpProtocolType, os.environ.get("HTTP_PROTOCOL", "auto")),
    # The log level to use
    "log_level": cast(LogLevelType, os.environ.get("LOG_LEVEL", "info")),
    # Whether to enable auto-reloading when code changes
    "reload": _get_env_bool("RELOAD", True),
    # Whether to enable threading
    "threading": _get_env_bool("THREADING", False),
    # Whether to enable access logging
    "access_log": _get_env_bool("ACCESS_LOG", True),
    # The server to use (auto, uvicorn, or granian)
    "server": cast(ServerType, os.environ.get("SERVER", "auto")),
}
