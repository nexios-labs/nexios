import sys
from pathlib import Path

from nexios.file_router.html import configure_templates

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(BASE_DIR))

from nexios import get_application
from nexios.file_router import FileRouter

app = get_application()

FileRouter(app, config={"root": "./routes", "exempt_paths": ["./routes/posts"]})

configure_templates(template_dir="templates")
