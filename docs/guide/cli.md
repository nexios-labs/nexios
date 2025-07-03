#  CLI Tools

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

1.  Using the `nexios` command (recommended):

    ```bash
    nexios [command]
    ```
2.  Using Python's module runner:

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

* `--output-dir, -o`: Directory where the project should be created (default: current directory)
* `--title`: Display title for the project (defaults to project name)
* `--template, -t`: Template type to use for the project (choices: basic, standard, beta, default: basic)

### Running the Development Server

```bash
nexios run
```

Options:

* `--app, -a`: Application import path (default: main:app)
* `--host`: Host to bind the server to (default: 127.0.0.1)
* `--port, -p`: Port to bind the server to (default: 4000)
* `--reload` : Enable auto-reload (default: enabled)
* `--workers`: Number of worker processes (default: 1)
* `--server`: Server to use for running the application (choices: auto, uvicorn, granian, default: auto)

### Listing All Registered URLs

```bash
nexios urls
```

Displays all registered routes in your application with their HTTP methods, paths, and handler information.

Options:

* `--app, -a`: Application import path (default: auto-detected from nexios.cli.py or main:app)
* `--config, -c`: Path to configuration file (default: nexios.cli.py in current directory)
* `--format, -f`: Output format (choices: table, json, yaml, default: table)
* `--methods`: Filter by HTTP methods (comma-separated, e.g., "GET,POST")
* `--path-prefix`: Filter routes by path prefix

Examples:

```bash
# List all URLs in table format
nexios urls

# List URLs in JSON format
nexios urls --format json

# List only GET and POST routes
nexios urls --methods GET,POST

# List routes with specific app
nexios urls --app myapp:app

# List routes starting with /api
nexios urls --path-prefix /api
```

### Checking Route Existence

```bash
nexios ping [PATH]
```

Checks if a specific route exists in your application and provides detailed information about it.

Options:

* `--app, -a`: Application import path (default: auto-detected from nexios.cli.py or main:app)
* `--config, -c`: Path to configuration file (default: nexios.cli.py in current directory)
* `--method, -m`: HTTP method to check (default: GET)
* `--verbose, -v`: Show detailed route information

Examples:

```bash
# Check if /api/users route exists
nexios ping /api/users

# Check POST method for /api/users
nexios ping /api/users --method POST

# Check with verbose output
nexios ping /api/users --verbose

# Check route with specific app
nexios ping /api/users --app myapp:app
```

### Interactive Development Shell

```bash
nexios shell
```

Launches an interactive Python shell with your Nexios application pre-loaded, allowing you to explore and test your application programmatically.

Options:

* `--app, -a`: Application import path (default: auto-detected from nexios.cli.py or main:app)
* `--config, -c`: Path to configuration file (default: nexios.cli.py in current directory)
* `--ipython`: Use IPython shell if available (default: auto-detect)
* `--bpython`: Use bpython shell if available (default: auto-detect)

Examples:

```bash
# Start interactive shell
nexios shell

# Use specific app
nexios shell --app myapp:app

# Force IPython shell
nexios shell --ipython
```

The shell provides access to:
- Your application instance (`app`)
- All registered routes (`app.routes`)
- Request/response utilities
- Database connections (if configured)
- Any other application dependencies

### Display Version Information

```bash
nexios version
```

Displays the Nexios version and ASCII art logo.

## Configuration File Support

The CLI automatically looks for a `nexios.cli.py` file in the current directory to load your application instance. This file should export an `app` variable:

```python
# nexios.cli.py
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")
async def home():
    return {"message": "Hello World"}
```

This allows the CLI to work with your specific application configuration without requiring manual app path specification.

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

1.  Create a new project:

    ```bash
    nexios new myproject
    cd myproject
    ```
2.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```
3.  Run the development server:

    ```bash
    nexios run
    ```
4.  Explore your routes:

    ```bash
    nexios urls
    ```
5.  Test specific routes:

    ```bash
    nexios ping /api/users
    ```
6.  Use interactive shell for debugging:

    ```bash
    nexios shell
    ```

The server will start with auto-reload enabled by default. Any changes to your code will automatically restart the server.

## Environment Variables

The `.env` file in your project supports the following variables:

* `DEBUG`: Enable/disable debug mode (default: True)
* `HOST`: Server host (default: 127.0.0.1)
* `PORT`: Server port (default: 4000)

You can add your own environment variables to this file, and they will be available to your application.

## Using with Poetry

If you're using Poetry for dependency management:

1.  Create a new project:

    ```bash
    nexios new myproject
    cd myproject
    ```
2.  Initialize Poetry and install dependencies:

    ```bash
    poetry install
    ```
3.  Run the development server:

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
nexios run --server uvicorn --workers 4  --host 0.0.0.0
```

#### Granian Example

```bash
nexios run --server granian 
```



**Installation**: Make sure to install Nexios with Granian support:

    ```bash
    pip install "nexios[granian]"
    ```


::: warning ⚠️ Warning

Granian Integration in nexios cli is not yet solid, use directly or use uvicorn

:::