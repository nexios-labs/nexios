from .base import MakeConfig
_global_config = None


def set_config(config :MakeConfig) -> None:
    global _global_config
    _global_config = config

def get_config() -> MakeConfig: 
    if _global_config is None:
        raise RuntimeError("Configuration has not been initialized.")
    return _global_config


DEFAULT_CONFIG = MakeConfig({
    "debug":True
})

