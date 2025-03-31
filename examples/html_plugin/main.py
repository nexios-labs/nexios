import sys
from pathlib import Path

from nexios.config.base import MakeConfig

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(BASE_DIR))

from nexios import get_application
from nexios.plugins import HTMLPlugin

app = get_application(MakeConfig({"secret_key": "hello"}))

HTMLPlugin(app, config={"root": "routes"})
