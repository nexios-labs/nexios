"""
Nexios templating system with Jinja2 integration.
"""

from typing import Any, Dict, Optional, Union, Callable
from pathlib import Path
import jinja2
from jinja2 import Environment, FileSystemLoader, select_autoescape

from nexios.config import MakeConfig
from nexios.http.response import HTMLResponse


class TemplateConfig(MakeConfig):
    """Template configuration settings."""

    def __init__(
        self,
        template_dir: Union[str, Path] = "templates",
        cache_size: int = 100,
        auto_reload: bool = True,
        encoding: str = "utf-8",
        enable_async: bool = True,
        trim_blocks: bool = True,
        lstrip_blocks: bool = True,
        custom_filters: Dict[str, Callable[[Any], Any]] = {},
        custom_globals: Dict[str, Any] = {},
    ):

        super().__init__(
            {
                "template_dir": template_dir,
                "cache_size": cache_size,
                "auto_reload": auto_reload,
                "encoding": encoding,
                "enable_async": enable_async,
                "trim_blocks": trim_blocks,
                "lstrip_blocks": lstrip_blocks,
                "custom_filters": custom_filters,
                "custom_globals": custom_globals,
            }
        )


class TemplateEngine:
    """Template engine for rendering Jinja2 templates."""

    def __init__(self, config: Optional[TemplateConfig] = None):
        self.config = config or TemplateConfig()
        self._setup_environment()

    def _setup_environment(self):
        """Initialize Jinja2 environment."""
        template_dir = Path(self.config.template_dir)
        template_dir.mkdir(parents=True, exist_ok=True)

        self.env = Environment(
            loader=FileSystemLoader(template_dir, encoding=self.config.encoding),
            autoescape=select_autoescape(["html", "xml"]),
            cache_size=self.config.cache_size,
            auto_reload=self.config.auto_reload,
            enable_async=self.config.enable_async,
            trim_blocks=self.config.trim_blocks,
            lstrip_blocks=self.config.lstrip_blocks,
        )

        filters = self.env.filters
        globals = self.env.globals
        config = self.config.to_dict()
        if config.get("custom_filters"):
            self.env.filters.update(config["custom_filters"])
        if config.get("custom_globals"):
            self.env.globals.update(config["custom_globals"])

    async def render(
        self, template_name: str, context: Optional[Dict[str, Any]] = None, **kwargs
    ) -> str:
        """Render a template with context."""
        context = context or {}
        context.update(kwargs)

        template = self.env.get_template(template_name)
        if self.config.enable_async:
            return await template.render_async(**context)
        return template.render(**context)


# Global engine instance
engine = TemplateEngine()


async def render(
    template_name: str,
    context: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> HTMLResponse:
    """Render template to response."""
    content = await engine.render(template_name, context, **kwargs)
    headers = headers or {"Content-Type": "text/html"}
    return HTMLResponse(content=content, status_code=status_code, headers=headers)
