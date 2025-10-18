"""
Tests for file-based session manager
"""
import pytest
import os
import tempfile
import json
import asyncio
from nexios.session.file import FileSessionManager
from nexios.config import MakeConfig, set_config


class TestFileSessionManager:
    """Test file-based session manager functionality"""

    def setup_method(self):
        """Set up test configuration with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        config = MakeConfig({
            "secret_key": "test-secret-key-for-file-sessions",
            "session": {
                "session_cookie_name": "test_session",
                "session_expiration_time": 3600,
                "session_permanent": False,
                "session_refresh_each_request": False,
                "session_file_storage_path": self.temp_dir,
                "session_file_name": "test_sessions"
            }
        })
        set_config(config)

    def teardown_method(self):
        """Clean up temporary directory"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_file_session_initialization(self):
        """Test file session manager initialization"""
        session = FileSessionManager("test-session-key")

        assert session.session_key == "test-session-key"
        assert session._session_cache == {}
        assert os.path.exists(session.session_file_path) is False

    def test_file_session_save_and_load(self):
        """Test saving and loading session data"""
        session = FileSessionManager("test-key-1")

        # Set some data
        session["user_id"] = 123
        session["preferences"] = {"theme": "dark"}

        # Save the session
        session.save()

        # Verify file was created
        assert os.path.exists(session.session_file_path)

        # Create new session and load data
        new_session = FileSessionManager("test-key-1")
        new_session.load()

        assert new_session["user_id"] == 123
        assert new_session["preferences"] == {"theme": "dark"}

    def test_file_session_with_existing_file(self):
        """Test loading from existing session file"""
        session1 = FileSessionManager("test-key-2")

        # Create initial data
        session1["initial"] = "data"
        session1.save()

        # Modify in new session
        session2 = FileSessionManager("test-key-2")
        session2["initial"] = "modified_data"
        session2["new_key"] = "new_value"
        session2.save()

        # Load and verify
        session3 = FileSessionManager("test-key-2")
        session3.load()

        assert session3["initial"] == "modified_data"
        assert session3["new_key"] == "new_value"

    def test_file_session_file_path_generation(self):
        """Test session file path generation"""
        session = FileSessionManager("custom-key")

        expected_path = os.path.join(self.temp_dir, "custom-key.json")
        assert session.session_file_path == expected_path

    def test_file_session_directory_creation(self):
        """Test that session directory is created if it doesn't exist"""
        custom_dir = os.path.join(self.temp_dir, "custom_sessions")
        config = MakeConfig({
            "secret_key": "test-secret-key",
            "session": {
                "session_file_storage_path": custom_dir
            }
        })
        set_config(config)

        session = FileSessionManager("test-key")
        assert os.path.exists(custom_dir)

    def test_file_session_corrupted_data(self):
        """Test handling of corrupted session file"""
        session = FileSessionManager("corrupted-key")

        # Create corrupted JSON file
        with open(session.session_file_path, 'w') as f:
            f.write("invalid json content")

        # Should handle gracefully
        session.load()
        assert session._session_cache == {}

    def test_file_session_missing_file(self):
        """Test loading when session file doesn't exist"""
        session = FileSessionManager("nonexistent-key")

        # Should handle gracefully
        session.load()
        assert session._session_cache == {}

    def test_file_session_clear(self):
        """Test clearing session data and file"""
        session = FileSessionManager("clear-test")

        session["data"] = "test"
        session.save()

        # Verify file exists
        assert os.path.exists(session.session_file_path)

        # Clear the session
        session.clear()

        # File should be removed
        assert os.path.exists(session.session_file_path) is False
        assert session._session_cache == {}

    def test_file_session_operations(self):
        """Test various session operations"""
        session = FileSessionManager("operations-test")

        # Test set_session and get_session
        session.set_session("key1", "value1")
        assert session.get_session("key1") == "value1"

        # Test get_all
        session.set_session("key2", "value2")
        items = dict(session.get_all())
        assert items == {"key1": "value1", "key2": "value2"}

        # Test keys and values
        assert set(session.keys()) == {"key1", "key2"}
        assert set(session.values()) == {"value1", "value2"}

        # Test is_empty
        assert session.is_empty() is False

        # Clear and test empty
        session.clear()
        assert session.is_empty() is True

    def test_file_session_concurrent_access(self):
        """Test concurrent access to session files"""
        session1 = FileSessionManager("concurrent-test")

        # Session 1 sets data
        session1["counter"] = 1
        session1.save()

        # Session 2 reads and modifies
        session2 = FileSessionManager("concurrent-test")
        session2.load()
        session2["counter"] = 2
        session2.save()

        # Session 3 reads final value
        session3 = FileSessionManager("concurrent-test")
        session3.load()
        assert session3["counter"] == 2

    def test_file_session_large_data(self):
        """Test session with large data"""
        session = FileSessionManager("large-data-test")

        # Create large data
        large_data = {"data": "x" * 10000, "list": list(range(1000))}
        session["large"] = large_data
        session.save()

        # Load and verify
        new_session = FileSessionManager("large-data-test")
        new_session.load()
        assert new_session["large"] == large_data

    def test_file_session_key_generation(self):
        """Test session key generation"""
        session = FileSessionManager()

        # Initially no key
        assert session.session_key is None

        # After setting data and saving, should have a key
        session["test"] = "value"
        session.save()

        assert session.session_key is not None
        assert isinstance(session.session_key, str)

    def test_file_session_with_special_characters(self):
        """Test session with special characters in data"""
        session = FileSessionManager("special-chars-test")

        special_data = {
            "unicode": "测试数据 🚀",
            "symbols": "!@#$%^&*()",
            "nested": {"key": "value with émojis 🔥"}
        }

        session["special"] = special_data
        session.save()

        # Load and verify
        new_session = FileSessionManager("special-chars-test")
        new_session.load()
        assert new_session["special"] == special_data
