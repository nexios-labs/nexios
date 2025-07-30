# Nexios CLI & Configuration Guide

Nexios provides a powerful, unified CLI for development, debugging, and deployment. The CLI is fully driven by a single configuration file: `nexios.config.py`.

## Prerequisites

Before using the Nexios CLI, you need to install the required dependencies:

```bash
pip install nexios[cli]
```

This will install `click`, which is required for all CLI functionality.

---

## 📦 Project Configuration: `nexios.config.py`

All CLI and server options are set as **plain variables** in `nexios.config.py` at your project root. This file is the single source of truth for how your app is run, introspected, and debugged.

### Example: Minimal Development Config

```python
# nexios.config.py
app_path = "main:app"      # Path to your app instance (module:variable)
server = "uvicorn"         # Server to use (uvicorn, granian, gunicorn)
port = 8000                # Port to bind
host = "127.0.0.1"         # Host to bind
reload = True              # Enable auto-reload (dev only)
```

### Example: Production with Gunicorn

```python
# nexios.config.py
app_path = "myproject.main:app"
server = "gunicorn"
port = 80
host = "0.0.0.0"
workers = 4
log_level = "info"
```

### Example: Custom Command

```python
# nexios.config.py
app_path = "src.main:app"
custom_command = "gunicorn -w 8 -b 0.0.0.0:8080 src.main:app"
```

---

## 🔑 Supported Config Variables

| Variable         | Type | Description                                                                |
| ---------------- | ---- | -------------------------------------------------------------------------- |
| `app_path`       | str  | **Required.** Path to your app instance, e.g. `main:app` or `src.main:app` |
| `server`         | str  | Server to use: `uvicorn`, `granian`, or `gunicorn`                         |
| `port`           | int  | Port to bind the server to                                                 |
| `host`           | str  | Host to bind the server to                                                 |
| `reload`         | bool | Enable auto-reload (dev only, uvicorn)                                     |
| `workers`        | int  | Number of worker processes (granian/gunicorn)                              |
| `log_level`      | str  | Log level for the server                                                   |
| `custom_command` | str  | If set, this command is run instead of built-in server logic               |
| ...              | ...  | Any other variables you want to use in your project                        |

---

## 🚀 CLI Commands & How They Use Config

All CLI commands automatically load `nexios.config.py` and use the variables you set:

- **`nexios run`**: Starts your app using `app_path` and all other config. If `custom_command` is set, it is used. If `server` is `gunicorn`, Gunicorn is used. Otherwise, Uvicorn or Granian is used.
- **`nexios dev`**: Like `run`, but always enables debug, reload, and verbose logging.
- **`nexios urls`**: Lists all registered routes. Uses `app_path` to load your app instance for introspection.
- **`nexios ping /route`**: Checks if a route exists. Uses `app_path` to load your app instance.
- **`nexios shell`**: Starts an interactive shell with your app loaded, using `app_path`.

You do **not** need to define an `app` variable in your config unless you want to use it for advanced scripting. The CLI will always use `app_path` to find and load your app instance.

---

## 🧑‍💻 Example Workflows

### 1. **Development**

```python
# nexios.config.py
app_path = "main:app"
server = "uvicorn"
port = 5050
host = "127.0.0.1"
reload = True
```

```bash
nexios run
nexios dev
nexios shell
nexios urls
nexios ping /about
```

### 2. **Production (Gunicorn)**

```python
# nexios.config.py
app_path = "src.main:app"
server = "gunicorn"
port = 80
host = "0.0.0.0"
workers = 8
log_level = "info"
```

```bash
nexios run
```

### 3. **Custom Command**

```python
# nexios.config.py
app_path = "myproject.main:app"
custom_command = "gunicorn -w 4 -b 0.0.0.0:9000 myproject.main:app"
```

```bash
nexios run
```

---

## ⚡️ Advanced: app vs. app_path

- `app_path` (recommended): The string path to your app instance, e.g. `main:app`. Used by all CLI commands to dynamically import your app.
- `app` (optional): If you want to use your app instance directly in Python scripts or for advanced CLI scripting, you can define it in `nexios.config.py`. Otherwise, it is not needed.

---

## 🛠️ Troubleshooting & Migration

- **Error: Could not find app module**: Make sure `app_path` is set in `nexios.config.py` and points to a valid module:variable.
- **Error: Could not load the app instance**: Check that your `app_path` is correct and the module is importable.
- **Switching from old config**: Just move your options to plain variables in `nexios.config.py` and set `app_path`.
- **Custom server logic**: Use `custom_command` for full control.

---

## 📝 Best Practices

- Always set `app_path` in your config for maximum compatibility.
- Use `server = "gunicorn"` for production, `uvicorn` for development.
- Use `nexios dev` for local development with auto-reload and debug.
- Use `nexios shell` for interactive debugging and testing.
- Keep your config expressive and version-controlled.

---

## 📚 Further Reading

- [Nexios Routing](./routing.md)
- [Nexios Middleware](./middleware.md)
- [Nexios Configuration Reference](./configuration.md)
- [Nexios URL Configuration](./url-configuration.md)

---

With this setup, Nexios CLI is fully driven by your project config, making development, debugging, and deployment seamless and consistent.
