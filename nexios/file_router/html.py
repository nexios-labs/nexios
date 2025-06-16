import functools
import inspect
import os
from os.path import exists, getmtime, join
from typing import Any, Dict, Optional

try:
    from jinja2 import BaseLoader, Environment, TemplateNotFound, select_autoescape
except ImportError:
    raise ImportError(
        "Jinja2 is not installed. Please install it with 'pip install jinja2'."
    )
from nexios.http import Request, Response
from nexios.logging import create_logger

logger = create_logger("nexios")

# Global template environment settings
DEFAULT_TEMPLATE_ENV: Optional[Environment] = None
DEFAULT_TEMPLATE_DIR: Optional[str] = None


class Loader(BaseLoader):
    def __init__(self, path: str):
        self.path = path

    def get_source(self, environment, template):
        path = join(self.path, template)
        if not exists(path):
            raise TemplateNotFound(template)
        mtime = getmtime(path)
        with open(path) as f:
            source = f.read()
        return source, path, lambda: mtime == getmtime(path)


def configure_templates(
    template_dir: Optional[str] = None,
    env: Optional[Environment] = None,
    **env_options: Dict[str, Any],
) -> None:
    """
    Configure global template settings.

    Args:
        template_dir: Default directory for templates
        env: Custom Jinja2 environment (overrides template_dir if provided)
        env_options: Additional options for creating default environment
    """
    global DEFAULT_TEMPLATE_ENV, DEFAULT_TEMPLATE_DIR

    if env is not None:
        DEFAULT_TEMPLATE_ENV = env
        DEFAULT_TEMPLATE_DIR = None
    elif template_dir is not None:
        DEFAULT_TEMPLATE_DIR = template_dir
        DEFAULT_TEMPLATE_ENV = Environment(
            loader=Loader(template_dir),
            autoescape=select_autoescape(),
            auto_reload=True,
            **env_options,  # type:ignore
        )
    else:
        DEFAULT_TEMPLATE_ENV = None
        DEFAULT_TEMPLATE_DIR = None


def render(template_path: str = "route.html"):
    """
    Decorator to render a Jinja2 template with the function's return context.
    Uses globally configured template settings if available, otherwise falls back to caller's directory.
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(req: Request, res: Response, *args, **kwargs):
            ctx = await func(req, res, *args, **kwargs)
            if not ctx:
                return ctx

            if not isinstance(ctx, dict):
                raise ValueError("The decorated function must return a dictionary.")

            # Use global environment if available
            if DEFAULT_TEMPLATE_ENV is not None:
                template_env = DEFAULT_TEMPLATE_ENV
            else:
                # Determine template directory
                template_directory = DEFAULT_TEMPLATE_DIR

                if template_directory is None:
                    stack = inspect.stack()

                    caller_frame = stack[1]  # The caller's frame
                    caller_module = inspect.getmodule(caller_frame[0])
                    template_directory = os.path.dirname(
                        os.path.abspath(caller_module.__file__)
                    )  # type:ignore

                template_env = Environment(
                    loader=Loader(template_directory),
                    autoescape=select_autoescape(),
                    auto_reload=True,
                )

            return res.html(template_env.get_template(template_path).render(**ctx))

        return wrapper

    return decorator
