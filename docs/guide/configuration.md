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