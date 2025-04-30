from .base import MakeConfig, DEFAULT_SERVER_CONFIG, SERVER_VALIDATION
from typing import Dict, Any

_global_config = None


def set_config(config: MakeConfig) -> None:
    global _global_config
    _global_config = config


def get_config() -> MakeConfig:
    if _global_config is None:
        raise RuntimeError("Configuration has not been initialized.")
        # return {}
    return _global_config


# Apply server validation to nested server configuration
def validate_server_config(config: Dict[str, Any]) -> bool:
    """Validate server configuration structure and values."""
    if not isinstance(config, dict):
        return False

    # Check each key in the server config
    for key, value in config.items():
        if key in SERVER_VALIDATION and not SERVER_VALIDATION[key](value):
            return False

    return True


DEFAULT_CONFIG = MakeConfig(
    {"debug": True, "server": DEFAULT_SERVER_CONFIG},
    validate={"server": validate_server_config},
)
