# CLI Tools

Nexios comes with a powerful CLI tool that helps you bootstrap new projects and manage development servers. It supports multiple server engines (Uvicorn by default, with optional Granian support) to run your ASGI applications.

## Installation

The CLI tool is automatically installed when you install Nexios:

```bash
pip install nexios  # Installs with Uvicorn by default
```

To install with Granian server support:

```bash
pip install "nexios[granian]"  # Install Nexios with optional Granian support
```

## Usage

You can invoke the CLI in two ways:

1. Using the `nexios` command (recommended):
   ```bash
   nexios [command]
   ```

2. Using Python's module runner:
   ```bash
   python -m nexios [command]
   ```

Both methods provide the same functionality. The first method is recommended for regular use, while the second method can be useful in environments where command-line scripts are not properly installed or when you need to ensure you're using a specific Python interpreter.

## Commands

### Creating a New Project

```bash
nexios new PROJECT_NAME
```

Options:
- `--output-dir, -o`: Directory where the project should be created (default: current directory)
- `--title`: Display title for the project (defaults to project name)

### Running the Development Server

```bash
nexios run
```

Options:
- `--app, -a`: Application import path (default: main:app)
- `--host`: Host to bind the server to (default: 127.0.0.1)
- `--port, -p`: Port to bind the server to (default: 4000)
- `--reload/--no-reload`: Enable/disable auto-reload (default: enabled)
- `--log-level`: Log level for the server (default: info)
- `--workers`: Number of worker processes (default: 1)
- `--server`: Server to use for running the application (choices: auto, uvicorn, granian, default: auto)
- `--access-log/--no-access-log`: Enable/disable access logging (default: enabled)

Granian-specific options:
- `--interface`: Server interface type (choices: asgi, wsgi, asgi-http, default: asgi)
- `--http-protocol`: HTTP protocol to use (choices: h11, h2, auto, default: auto)
- `--threading/--no-threading`: Enable/disable threading (default: disabled)

### Display Version Information

```bash
nexios version
```

Displays the Nexios version and ASCII art logo.

## Project Structure

When you create a new project with `nexios new`, it generates the following structure:

```
project_name/
├── main.py           # Application entry point
├── requirements.txt  # Project dependencies
├── README.md         # Project documentation
├── .gitignore        # Git ignore rules
└── .env              # Environment variables
```

## Development Workflow

1. Create a new project:
   ```bash
   nexios new myproject
   cd myproject
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   nexios run
   ```

The server will start with auto-reload enabled by default. Any changes to your code will automatically restart the server.

## Environment Variables

The `.env` file in your project supports the following variables:
- `DEBUG`: Enable/disable debug mode (default: True)
- `HOST`: Server host (default: 127.0.0.1)
- `PORT`: Server port (default: 4000)

You can add your own environment variables to this file, and they will be available to your application.

## Using with Poetry

If you're using Poetry for dependency management:

1. Create a new project:
   ```bash
   nexios new myproject
   cd myproject
   ```

2. Initialize Poetry and install dependencies:
   ```bash
   poetry install
   ```

3. Run the development server:
   ```bash
   poetry run nexios run
   ```

## Common Issues and Solutions

### Port Already in Use

If you see an error like "Port 4000 is already in use", try using a different port:

```bash
nexios run --port 5000
```

### Module Not Found

If you get a "Module not found" error, make sure you're running the command from the project root directory or specify the correct application path:

```bash
nexios run --app mymodule:app
```

### Customizing the Server

For production deployments, you might want to disable auto-reload and increase the number of workers:

```bash
nexios run --no-reload --workers 4 --host 0.0.0.0
```

## Server Selection

Nexios now supports multiple server engines for running your applications:

### Automatic Server Selection

By default, Nexios will automatically use the best available server in this order:

1. Uvicorn (default if installed)
2. Granian (used if Uvicorn is not installed)

```bash
# Uses the best available server (Uvicorn by default)
nexios run
```

### Explicit Server Selection

You can explicitly choose which server to use:

```bash
# Use Uvicorn server
nexios run --server uvicorn

# Use Granian server
nexios run --server granian
```

### Server-specific Configuration

#### Uvicorn Example

```bash
nexios run --server uvicorn --workers 4 --log-level debug --host 0.0.0.0
```

#### Granian Example

```bash
nexios run --server granian --interface asgi --http-protocol h2 --threading
```

### Configuration in .env or Configuration Files

You can also set the server preference in your application's configuration:

```python
# In your config file
server_config = {
    "host": "0.0.0.0",
    "port": 8000,
    "server": "uvicorn",  # or "granian"
    "workers": 2,
    "log_level": "info"
}
```

## For Existing Granian Users

If you have existing applications built with earlier versions of Nexios that used Granian by default:

1. **No action required**: Your applications will continue to work if Granian is installed.

2. **Explicit server selection**: To ensure your application continues to use Granian:
   ```bash
   nexios run --server granian
   ```

3. **Configuration update**: Update your configuration to explicitly set Granian as the server:
   ```python
   server_config = {
       # other options...
       "server": "granian"
   }
   ```

4. **Installation**: Make sure to install Nexios with Granian support:
   ```bash
   pip install "nexios[granian]"
   ```

