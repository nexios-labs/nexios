from nexios.config import MakeConfig

try:
    import os

    from dotenv import load_dotenv

    load_dotenv()
    env_config = {key: value for key, value in os.environ.items()}
except ImportError:
    env_config = {}

default_config = {
    "debug": True,
    "title": "{{project_name_title}}",
}

# Merge env config into default config
# Env config will override default if same keys exist
merged_config = {**default_config, **env_config}

app_config = MakeConfig(merged_config)
