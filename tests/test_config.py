# test_config.py

import pytest

from nexios.config import MakeConfig, get_config, set_config


# Test MakeConfig class
def test_makeconfig_initialization():
    # Test basic initialization
    config = MakeConfig({"debug": True, "db": {"host": "localhost"}})
    assert config.debug is True
    assert config.db.host == "localhost"

    # Test with defaults
    config = MakeConfig(
        {"debug": False}, defaults={"debug": True, "db": {"port": 5432}}
    )
    assert config.debug is False  # Overrides default
    assert config.db.port == 5432  # From defaults

    # Test immutable config
    config = MakeConfig({"debug": True}, immutable=True)
    with pytest.raises(AttributeError):
        config.debug = False


def test_makeconfig_nested_access():
    config = MakeConfig({"app": {"name": "MyApp", "settings": {"timeout": 30}}})

    # Test attribute access
    assert config.app.name == "MyApp"
    assert config.app.settings.timeout == 30

    # Test dictionary-style access
    assert config["app.name"] == "MyApp"
    assert config["app.settings.timeout"] == 30
    assert config["nonexistent.key"] is None


def test_makeconfig_conversion_methods():
    config = MakeConfig({"debug": True, "db": {"host": "localhost", "port": 5432}})

    # Test to_dict
    config_dict = config.to_dict()
    assert config_dict == {"debug": True, "db": {"host": "localhost", "port": 5432}}

    # Test to_json
    config_json = config.to_json()
    assert '"debug": true' in config_json
    assert '"host": "localhost"' in config_json


def test_makeconfig_repr():
    config = MakeConfig({"debug": True})
    assert repr(config) == "MakeConfig({'debug': True})"


def test_config_immutability():
    # Create mutable config
    config = MakeConfig({"debug": True})
    set_config(config)

    # Should be able to modify
    get_config().debug = False
    assert get_config().debug is False

    # Create immutable config
    immutable_config = MakeConfig({"debug": True}, immutable=True)
    set_config(immutable_config)

    # Should not be able to modify
    with pytest.raises(AttributeError):
        get_config().debug = False


# Test edge cases
def test_makeconfig_edge_cases():
    # Test empty config
    empty_config = MakeConfig({})
    assert empty_config.to_dict() == {}

    # Test None values
    config_with_none = MakeConfig({"debug": None})
    assert config_with_none.debug is None

    # Test non-dict values
    config = MakeConfig({"version": "1.0"})
    assert config.version == "1.0"


def test_makeconfig_nested_immutability():
    # Test nested immutability
    config = MakeConfig({"db": {"host": "localhost"}}, immutable=True)

    with pytest.raises(AttributeError):
        config.db.host = "127.0.0.1"
