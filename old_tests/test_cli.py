import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import click
import pytest

from nexios.cli import cli
from nexios.cli.commands import (
    new,
    run,
)
from nexios.cli.utils import (
    _check_server_installed,
    _echo_error,
    _echo_info,
    _echo_success,
    _echo_warning,
    _find_app_module,
    _has_write_permission,
    _is_port_in_use,
    _validate_app_path,
    _validate_host,
    _validate_port,
    _validate_project_name,
    _validate_project_title,
    _validate_server,
)


class TestCLIUtilityFunctions:
    """Test CLI utility functions"""

    def test_echo_success(self, capsys):
        _echo_success("Test success")
        captured = capsys.readouterr()
        assert "✓ Test success" in captured.out

    def test_echo_error(self, capsys):
        _echo_error("Test error")
        captured = capsys.readouterr()
        assert "✗ Test error" in captured.err

    def test_echo_info(self, capsys):
        _echo_info("Test info")
        captured = capsys.readouterr()
        assert "ℹ Test info" in captured.out

    def test_echo_warning(self, capsys):
        _echo_warning("Test warning")
        captured = capsys.readouterr()
        assert "⚠ Test warning" in captured.out

    def test_has_write_permission(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        assert _has_write_permission(test_file) is True

    @patch("socket.socket")
    def test_is_port_in_use_true(self, mock_socket):
        mock_socket.return_value.__enter__.return_value.connect_ex.return_value = 0
        assert _is_port_in_use("localhost", 8000) is True

    @patch("socket.socket")
    def test_is_port_in_use_false(self, mock_socket):
        mock_socket.return_value.__enter__.return_value.connect_ex.return_value = 1
        assert _is_port_in_use("localhost", 8000) is False

    @patch("subprocess.run")
    def test_check_server_installed_true(self, mock_run):
        mock_run.return_value.returncode = 0
        assert _check_server_installed("uvicorn") is True

    @patch("subprocess.run")
    def test_check_server_installed_false(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        assert _check_server_installed("nonexistent") is False

    @patch("subprocess.run")
    def test_check_server_installed_called_process_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "test")
        assert _check_server_installed("test") is False


class TestCLIValidationFunctions:
    """Test CLI validation functions"""

    def test_validate_project_name_valid(self):
        ctx = Mock()
        param = Mock()
        result = _validate_project_name(ctx, param, "valid_project")
        assert result == "valid_project"

    def test_validate_project_name_invalid(self):
        ctx = Mock()
        param = Mock()
        with pytest.raises(click.BadParameter):
            _validate_project_name(ctx, param, "invalid-project")

    def test_validate_project_name_empty(self):
        ctx = Mock()
        param = Mock()
        result = _validate_project_name(ctx, param, "")
        assert result == ""

    def test_validate_project_title_valid(self):
        ctx = Mock()
        param = Mock()
        result = _validate_project_title(ctx, param, "Valid Title")
        assert result == "Valid Title"

    def test_validate_project_title_invalid(self):
        ctx = Mock()
        param = Mock()
        with pytest.raises(click.BadParameter):
            _validate_project_title(ctx, param, "Invalid@Title")

    def test_validate_host_valid(self):
        ctx = Mock()
        param = Mock()
        result = _validate_host(ctx, param, "localhost")
        assert result == "localhost"

    def test_validate_host_invalid(self):
        ctx = Mock()
        param = Mock()
        with pytest.raises(click.BadParameter):
            _validate_host(ctx, param, "invalid@host")

    def test_validate_port_valid(self):
        ctx = Mock()
        param = Mock()
        result = _validate_port(ctx, param, 8000)
        assert result == 8000

    def test_validate_port_invalid_low(self):
        ctx = Mock()
        param = Mock()
        with pytest.raises(click.BadParameter):
            _validate_port(ctx, param, 0)

    def test_validate_port_invalid_high(self):
        ctx = Mock()
        param = Mock()
        with pytest.raises(click.BadParameter):
            _validate_port(ctx, param, 70000)

    def test_validate_app_path_valid(self):
        ctx = Mock()
        param = Mock()
        result = _validate_app_path(ctx, param, "main:app")
        assert result == "main:app"

    def test_validate_app_path_invalid(self):
        ctx = Mock()
        param = Mock()
        with pytest.raises(click.BadParameter):
            _validate_app_path(ctx, param, "invalid:path:format")

    def test_validate_server_valid(self):
        ctx = Mock()
        param = Mock()
        result = _validate_server(ctx, param, "uvicorn")
        assert result == "uvicorn"

    def test_validate_server_invalid(self):
        ctx = Mock()
        param = Mock()
        with pytest.raises(click.BadParameter):
            _validate_server(ctx, param, "invalid_server")


class TestCLIHelperFunctions:
    """Test CLI helper functions"""

    def test_find_app_module_main_py(self, tmp_path):
        main_py = tmp_path / "main.py"
        main_py.write_text("app = None")
        result = _find_app_module(tmp_path)
        assert result == "main:app"

    def test_find_app_module_app_main_py(self, tmp_path):
        app_dir = tmp_path / "app"
        app_dir.mkdir()
        main_py = app_dir / "main.py"
        main_py.write_text("app = None")
        result = _find_app_module(tmp_path)
        assert result == "app.main:app"

    def test_find_app_module_src_main_py(self, tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        main_py = src_dir / "main.py"
        main_py.write_text("app = None")
        result = _find_app_module(tmp_path)
        assert result == "src.main:app"

    def test_find_app_module_not_found(self, tmp_path):
        result = _find_app_module(tmp_path)
        assert result is None


class TestCLIGroup:
    """Test CLI group functionality"""

    def test_cli_group_creation(self):
        """Test that the CLI group can be created"""
        assert cli.name == "cli"
        assert len(cli.commands) > 0

    def test_cli_has_new_command(self):
        """Test that the CLI has the new command"""
        assert "new" in cli.commands

    def test_cli_has_run_command(self):
        """Test that the CLI has the run command"""
        assert "run" in cli.commands
