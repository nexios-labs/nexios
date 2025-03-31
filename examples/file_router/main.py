import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(BASE_DIR))

from nexios import get_application
from nexios.plugins import FileRouterPlugin

app = get_application()

FileRouterPlugin(app, config={"root": "routes"})
