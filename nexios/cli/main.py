import os
import click
from subprocess import run as run_command
@click.group()
def nexios():
    """🚀 Nexios CLI - Your tool for quickly spinning up Nexios projects!"""
    pass




@nexios.command()
@click.option('--name', prompt='📂 Enter the project name', help='Name of the Nexios project')
@click.option('--full', is_flag=True, help='Install full Nexios package?')
@click.option('--extras', prompt='🔧 Enter any extra packages (comma-separated)', default='', help='Additional packages to install')
@click.option('--setup-db', is_flag=True, help='Set up a database for the project')
def init(name, full, extras, setup_db):
    """🎉 Initialize a new Nexios project."""

    # Step 1: Create project directory
    project_dir = os.path.abspath(name)
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
        click.secho(f"📂 Created project directory: {project_dir}", fg="green")
    else:
        click.secho("⚠️ Directory already exists. Using the existing one.", fg="red")

    requirements_path = os.path.join(project_dir, "requirements.txt")

    with open(requirements_path, 'w') as f:
        f.write("nexios\n")
        if setup_db:
            f.write("tortoise-orm\n")
        if full:
            f.write("nexios[full]\n")
        if extras:
            extra_packages = [pkg.strip() for pkg in extras.split(",")]
            f.write("\n".join(extra_packages))

    click.secho("📄 Created requirements.txt with dependencies:", fg="cyan")
    click.secho("- nexios", fg="green")
    if setup_db:
        click.secho("- tortoise-orm", fg="green")
    if full:
        click.secho("- nexios[full]", fg="green")
    if extras:
        click.secho(f"- {extras.replace(',', ', ')}", fg="green")



    controllers_dir = os.path.join(project_dir, "controllers")
    os.makedirs(controllers_dir, exist_ok=True)

    demo_controller_path = os.path.join(controllers_dir, "demo_controller.py")
    demo_init_path = os.path.join(controllers_dir, "__init__.py")

    with open(os.path.join(os.path.dirname(__file__),"templates/demo_controller.py")) as demo_controller:
        demo_controller_code = demo_controller.read()
    with open(demo_controller_path, 'w') as f:
        f.write(demo_controller_code)
    with open(demo_init_path, 'w') as f:
        f.write("""from .demo_controller import index""")
    click.secho(f"📝 Created demo controller at: {demo_controller_path}", fg="magenta")

    if setup_db:
        setup_database(project_dir)

    else:
        config_path = os.path.join(project_dir,"config.py")
        with open(config_path, 'w') as f:
            with  open(os.path.join(os.path.dirname(__file__),"templates/config.py")) as db_config:
                f.write(db_config.read())




    main_dir = os.path.join(project_dir, "main.py")
    with open(main_dir, 'w') as f:
        with open(os.path.join(os.path.dirname(__file__),"templates/main.py")) as db_config:
            f.write(db_config.read())

    click.secho(f"🎉 Nexios project '{name}' has been initialized successfully!", fg="green", bold=True)
    click.secho("🚀 Get started by navigating to your project directory!", fg="cyan", bold=True)

def setup_database(project_dir):
    """Set up a database configuration file."""

    db_type = click.prompt(
        "🗄️ Choose a database type",
        type=click.Choice(['sqlite3', 'postgresql', 'mysql'], case_sensitive=False),
        default='sqlite3'
    )

    db_name = click.prompt("📂 Enter the database name", default="db.sqlite3" if db_type == 'sqlite3' else "nexios_db")
    db_user = db_password = db_host = db_port = None
    db_driver = None  #

    if db_type in ['postgresql', 'mysql']:
        db_user = click.prompt(f"👤 Enter the {db_type} username", default="postgres" if db_type == 'postgresql' else "root")
        db_password = click.prompt(f"🔑 Enter the {db_type} password", hide_input=True, default="password")
        db_host = click.prompt(f"🌍 Enter the database host", default="localhost")
        db_port = click.prompt(f"📟 Enter the database port", default="5432" if db_type == 'postgresql' else "3306")
        db_driver = "asyncpg" if db_type == "postgresql" else "aiomysql"
    else:
        db_driver = "sqlite3"

    requirements_path = os.path.join(project_dir, "requirements.txt")
    with open(requirements_path, 'a') as f:
        if db_driver and db_driver != "sqlite3":
            f.write(f"\n{db_driver}")
            click.secho(f"📦 Added {db_driver} to requirements.txt", fg="green")

    config_path = os.path.join(project_dir, "config.py")
    with open(config_path, 'w') as f:
        if db_type == 'sqlite3':
            with open(os.path.join(os.path.dirname(__file__),"templates/config_db_sqlite3.py")) as db_config:
                data = db_config.read()
                f.write(data.format(db_name=db_name))
        else:
            with open(os.path.join(os.path.dirname(__file__),"templates/config_db.py")) as db_config:
                data = db_config.read()
                f.write(data.format(
                    db_user=db_user,
                    db_password=db_password,
                    db_host=db_host,
                    db_port=db_port,
                    db_name=db_name
                ))
    requirements_path = os.path.join(project_dir, "requirements.txt")
    click.secho("📦 Installing dependencies...", fg="blue", bold=True)
    run_command(["pip", "install", "-r", requirements_path])
    click.secho("✅ Dependencies installed!", fg="green", bold=True)
    click.secho(f"📝 Created database config at: {config_path}", fg="cyan")
    click.secho(f"📦 Database setup complete with {db_type} and driver {db_driver}!", fg="green", bold=True)



def find_app_file():
    possible_files = ["app.py", "main.py", "app/main.py"]
    for file in possible_files:
        if os.path.exists(file):
            return file
    return None
@nexios.command()
@click.option('--host', default='127.0.0.1', help='Host to run the server on')
@click.option('--port', default=8000, help='Port to run the server on')
@click.option('--reload', is_flag=True, help='Enable hot reload for development mode')
def run(host, port, reload):
    """Run the Uvicorn server."""
    app_file = find_app_file()

    if not app_file:
        click.secho("Could not find a valid ASGI app file (app.py, main.py, or app/main.py).", fg="red")

        # sys.exit(1)
    command = ["uvicorn", app_file.replace(".py", ":app"), "--host", host, "--port", str(port)]

    if reload:
        command.append("--reload")

    os.system(" ".join(command))
@nexios.command()
@click.option('--host', default='127.0.0.1', help='Host to run the server on')
@click.option('--port', default=8000, help='Port to run the server on')
def dev(host, port):
    """Run the Uvicorn server in development mode (hot reload)."""
    # Passing the --reload flag directly in development mode
    run(host=host, port=port, reload=True)

if __name__ == "__main__":
    nexios()
