from tempfile import template
from nexios.templating import TemplateConfig
import os

try:

    from dotenv import load_dotenv

    load_dotenv()
    env_config = {key: value for key, value in os.environ.items()}
except ImportError:
    env_config = {}

title = "{{project_name_title}}"


templating = TemplateConfig(template_dir="templates")
