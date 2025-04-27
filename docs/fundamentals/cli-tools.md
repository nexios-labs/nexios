# CLI Tools

Nexios comes with a powerful CLI tool that helps you bootstrap new projects and manage development servers.

## Installation

The CLI tool is automatically installed when you install Nexios:

```bash
pip install nexios
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

