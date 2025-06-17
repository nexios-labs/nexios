import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .base import BaseSessionInterface


class FileSessionManager(BaseSessionInterface):
    def __init__(self, session_key: str) -> None:
        super().__init__(session_key)
        self.session_key = session_key or self.get_session_key()
        self.session_file_path = os.path.join(
            self.session_config.session_file_name or "sessions",
            f"{self.session_key}.json",
        )

        # Ensure the session storage directory exists
        os.makedirs(
            self.session_config.session_file_storage_path or "sessions", exist_ok=True
        )

    def _load_session_data(self) -> Optional[Dict[str, Any]]:
        """Load session data from the file."""
        if os.path.exists(self.session_file_path):
            with open(self.session_file_path, "r") as file:
                try:
                    session_data = json.load(file)
                    return session_data
                except json.JSONDecodeError:
                    return None
        return None

    def _save_session_data(self):
        """Save the session data to a file."""
        with open(self.session_file_path, "w") as file:
            json.dump(self._session_cache, file)

    def set_session(self, key: str, value: str):
        """Set a session value."""
        self.modified = True
        self._session_cache[key] = value

    def get_session(self, key: str) -> Optional[str]:
        """Get a session value."""
        return self._session_cache.get(key, None)

    def get_all(self):
        """Get all session data."""
        return self._session_cache.items()

    def keys(self):
        """Get all session keys."""
        return self._session_cache.keys()

    def values(self):
        """Get all session values."""
        return self._session_cache.values()

    def is_empty(self) -> bool:
        """Check if the session is empty."""
        return len(self._session_cache.items()) == 0

    async def save(self):  # type: ignore
        """Save the session data to the file."""
        self._save_session_data()

    @property
    def should_set_cookie(self) -> bool:
        """Determines if the cookie should be set."""
        return self.modified or (
            self.session_config.session_permanent
            and self.session_config.session_refresh_each_request
        )

    def has_expired(self) -> bool:
        """Returns True if the session has expired."""
        expiration_time = self.get_expiration_time()
        if expiration_time and datetime.now(timezone.utc) > expiration_time:  # type:ignore
            return True
        return False

    async def load(self):
        """Load the session data from the file."""
        session_data = self._load_session_data()

        if session_data:
            self._session_cache.update(session_data)
        else:
            self._session_cache = {}

    def clear(self):
        """Clear the session data."""
        self._session_cache.clear()
        if os.path.exists(self.session_file_path):
            os.remove(self.session_file_path)
