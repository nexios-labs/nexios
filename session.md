Session management is crucial for maintaining user state across requests in a web application. Nexios provides a flexible and scalable approach to session handling, supporting various backends such as in-memory storage, databases, and distributed caches.

## Basic Configuration


First sessions in nexios require `secret_key` key in the application configuration 

**Example Impementation**


```py

from nexios import get_application,MakeConfig

app_config = MakeConfig({
    "secret_key" : "super-secure"
})

app = get_applcation(config = app_config)

@app.get("/endpoint")
async def set_session(req, res):
    req.session.set_session("key", "value")
    return res.json({"sucess","session set"})



@app.get("/endpoint")
async def set_session(req, res):
    req.session.get_session("key")
    return res.json({"sucess","session set"})
```


## More Session configuration

```py

app_config = MakeConfig({
    "secret_key" : "super-secure",
    "session":{
        #more session configuration
    }
})


```

## Session Configuration Table

| Configuration                     | Description |
|------------------------------------|-------------|
| `session_cookie_name`             | The name of the session cookie. Defaults to `"session_id"` if not set. |
| `session_cookie_domain`           | The domain for which the session cookie is valid. |
| `session_cookie_path`             | The path for which the session cookie is valid. |
| `session_cookie_httponly`         | Determines if the session cookie should be HTTPOnly, preventing JavaScript access. |
| `session_cookie_secure`           | Specifies if the session cookie should be transmitted only over HTTPS. |
| `session_cookie_samesite`         | Defines the SameSite policy (`None`, `Lax`, or `Strict`). Helps prevent CSRF attacks. |
| `session_cookie_partitioned`      | Indicates if the cookie should be partitioned for improved security in cross-site contexts. |
| `session_expiration_time`         | Determines how long the session lasts before expiration. Defaults to `86400` minutes (1 day). |
| `session_permanent`               | If `True`, the session remains active across browser restarts. |
| `session_refresh_each_request`    | If `True`, resets the session expiration time on every request. |



## Full Example of Session Management in Nexios

```python
from nexios import get_application, MakeConfig

# Define application configuration with session settings
app_config = MakeConfig({
    "secret_key": "super-secure",  # Required for session encryption
    "session": {
        "session_cookie_name": "my_session",  # Custom session cookie name
        "session_cookie_httponly": True,  # Prevent JavaScript access
        "session_cookie_secure": True,  # Allow only HTTPS requests
        "session_cookie_samesite": "Lax",  # Mitigate CSRF attacks
        "session_expiration_time": 1440,  # Session expiration time in minutes
        "session_permanent": True,  # Make sessions persistent
        "session_refresh_each_request": True  # Refresh session on each request
    }
})

# Create Nexios application with the defined config
app = get_application(config=app_config)

@app.get("/set-session")
async def set_session(req, res):
    """Sets a session value"""
    req.session.set_session("username", "Dunamis")
    return res.json({"success": True, "message": "Session set!"})

@app.get("/get-session")
async def get_session(req, res):
    """Retrieves a session value"""
    username = req.session.get_session("username")
    return res.json({"success": True, "username": username})

@app.get("/delete-session")
async def delete_session(req, res):
    """Deletes a session key"""
    req.session.delete_session("username")
    return res.json({"success": True, "message": "Session deleted!"})

@app.get("/check-session")
async def check_session(req, res):
    """Checks if the session has expired"""
    expired = req.session.has_expired()
    return res.json({"expired": expired})

```
---
## Custom manager

By default, Nexios utilizes signed cookies for session storage, allowing lightweight and stateless management without requiring a database. However, for applications that need more robust session handling, Nexios provides additional backend options.

To switch session storage in Nexios, simply specify the manager key in the session configuration. By default, Nexios uses signed cookies, but you can change it to other backends like file storage or custom implementations.

**Example Configuration**

```py


from nexios import get_application, MakeConfig
from nexios.sessions.file import FileSessionManager

app_config = MakeConfig({
    "secret_key": "super-secure",
    "session": {
        "manager": FileSessionManager,  # Switch session storage to file-based
        "session_expiration_time": 1440,  # Set session expiration time in minutes
    }
})

app = get_application(config=app_config)

```

Nexios provides a flexible session management system that allows developers to extend and customize session storage. By default, it uses signed cookies, but developers can create a custom session manager by inheriting from BaseSessionInterface.

#### **Steps to Implement:**

* Inherit from BaseSessionInterface.

* Use an in-memory dictionary (_session_store) to hold session data.

* Implement expiration handling by storing timestamps.

* Override load to retrieve sessions.

* Override save to update session data.

```py


from typing import Dict, Any
from datetime import datetime, timedelta
from nexios.session.base import BaseSessionInterface

class MemorySessionManager(BaseSessionInterface):
    _session_store: Dict[str, Dict[str, Any]] = {}  # Store sessions in memory
    session_timeout = 1800  # 30 minutes expiration

    def __init__(self, session_key: str):
        super().__init__(session_key)
        self.load()

    def load(self):
        """Loads session data from memory if not expired."""
        session_data = self._session_store.get(self.session_key, None)
        if session_data:
            expires_at = session_data.get("expires_at")
            if expires_at and datetime.utcnow() > expires_at:
                del self._session_store[self.session_key]  # Expired, remove session
            else:
                self._session_cache = session_data.get("data", {})
        
    async def save(self):
        """Saves session data in memory with an expiration timestamp."""
        self._session_store[self.session_key] = {
            "data": self._session_cache,
            "expires_at": datetime.utcnow() + timedelta(seconds=self.session_timeout)
        }

```

## Using the Custom Session Manager

```py
from nexios import get_application, MakeConfig
from my_custom_session import MemorySessionManager

app_config = MakeConfig({
    "secret_key": "super-secure",
    "session": {
        "manager": MemorySessionManager  # Set the custom session manager
    }
})

app = get_application(config=app_config)

@app.get("/set-session")
async def set_session(req, res):
    req.session.set_session("username", "Dunamis")
    return res.json({"success": "Session set"})

@app.get("/get-session")
async def get_session(req, res):
    username = req.session.get_session("username")
    return res.json({"username": username})


```