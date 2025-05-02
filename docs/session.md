---
icon: server
---

# Session Management

## Session Management

Session management is a critical component of web applications, allowing you to store and retrieve user data across multiple requests. Nexios provides a robust, flexible session management system that's easy to configure yet powerful enough for complex applications.

### Introduction to Sessions

Sessions in Nexios allow you to maintain state for users as they navigate through your application. Common uses for sessions include:

* User authentication (storing logged-in state)
* Shopping carts and order processes
* User preferences and settings
* Multi-step form completion
* Temporary data storage

Nexios provides several options for session storage, secure cookie handling, and customization to fit your application's needs.

### Basic Session Setup

Setting up sessions in your Nexios application is straightforward:

```python
from nexios import get_application
from nexios.session.middleware import SessionMiddleware

app = get_application()

# Required: Configure a secret key for signing sessions
app.config.secret_key = "your-secure-secret-key"

# Add the session middleware
app.add_middleware(SessionMiddleware)
```

With this minimal setup, Nexios will use the default cookie-based session backend. Your routes can now access the session through the request object:

```python
@app.get("/")
async def index(req, res):
    # Access the session
    counter = req.session.get("counter", 0)
    counter += 1
    req.session["counter"] = counter
    
    return res.text(f"You've visited this page {counter} times")
```

### Session Configuration Options

Nexios offers various configuration options for customizing session behavior:

```python
from nexios import get_application
from nexios.session.middleware import SessionMiddleware
from nexios.session.file import FileSessionInterface

app = get_application()

# Required secret key for secure cookies
app.config.secret_key = "your-secure-secret-key"

# Session configuration
app.config.session = {
    # Session cookie name
    "session_cookie_name": "nexios_session",
    
    # Cookie settings
    "cookie_path": "/",
    "cookie_domain": None,
    "cookie_secure": True,
    "cookie_httponly": True,
    "cookie_samesite": "lax",
    
    # Session expiration (in seconds)
    "expiry": 86400,  # 24 hours
    
    # Session backend
    "manager": FileSessionInterface,
    
    # Backend-specific settings
    "directory": "sessions",
    "prefix": "session_"
}

# Add the session middleware
app.add_middleware(SessionMiddleware())
```

#### Configuration Options Reference

| Option                | Description                                           | Default                |
| --------------------- | ----------------------------------------------------- | ---------------------- |
| `session_cookie_name` | Name of the cookie storing the session ID             | `"session_id"`         |
| `cookie_path`         | Path for which the cookie is valid                    | `"/"`                  |
| `cookie_domain`       | Domain for which the cookie is valid                  | `None`                 |
| `cookie_secure`       | Whether cookie should only be sent over HTTPS         | `False`                |
| `cookie_httponly`     | Whether cookie should be accessible via JavaScript    | `True`                 |
| `cookie_samesite`     | SameSite attribute (`"lax"`, `"strict"`, or `"none"`) | `"lax"`                |
| `expiry`              | Session lifetime in seconds                           | `86400` (24 hours)     |
| `manager`             | Session backend class                                 | `SignedSessionManager` |

### Working with Sessions

#### Basic Session Operations

```python
@app.get("/session-demo")
async def session_demo(req, res):
    # Get a value with default if not present
    user_id = req.session.get("user_id", None)
    
    # Set a value
    req.session["last_visit"] = time.time()
    
    # Check if a key exists
    if "preferences" in req.session:
        preferences = req.session["preferences"]
    
    # Remove a key
    if "temporary_data" in req.session:
        del req.session["temporary_data"]
    
    # Clear the entire session
    # req.session.clear()
    
    return res.json({
        "user_id": user_id,
        "session_keys": list(req.session.keys())
    })
```

#### Session Properties and Methods

Sessions in Nexios behave similar to dictionaries but with additional methods:

| Method/Property                  | Description                                            |
| -------------------------------- | ------------------------------------------------------ |
| `session.get(key, default=None)` | Get a value, returning default if not present          |
| `session[key] = value`           | Set a session value                                    |
| `key in session`                 | Check if key exists in the session                     |
| `del session[key]`               | Delete a key from the session                          |
| `session.clear()`                | Remove all keys from the session                       |
| `session.keys()`                 | Get all keys in the session                            |
| `session.items()`                | Get all key-value pairs in the session                 |
| `session.pop(key, default=None)` | Get and remove a key, returning default if not present |
| `session.is_empty()`             | Check if session has no data                           |
| `session.modified`               | Whether session has been modified                      |

#### Session Expiration

By default, sessions expire after 24 hours (86400 seconds). You can customize this:

```python
# Set global session expiration time
app.config.session = {
    "expiry": 3600  # 1 hour
}

# Or set per-session expiration time
@app.post("/login")
async def login(req, res):
    # Authenticate user...
    req.session["user_id"] = user.id
    
    # Set this specific session to expire in 30 minutes
    req.session.set_expiry(1800)
    
    return res.json({"success": True})
```

### Session Backends

Nexios supports multiple session backends to store session data. Each backend has different characteristics suitable for various use cases.

#### Signed Cookie Sessions (Default)

The simplest session backend, storing the session data directly in a signed cookie:

```python
from nexios.session.signed_cookies import SignedSessionManager

app.config.session = {
    "manager": SignedSessionManager
}
```

**Pros**:

* No server-side storage required
* Works well in distributed environments
* Simple setup

**Cons**:

* Limited storage size (4KB cookie limit)
* Session data sent with every request
* Cannot be invalidated server-side

#### File-based Sessions

Stores session data in files on the server filesystem:

```python
from nexios.session.file import FileSessionInterface

app.config.session = {
    "manager": FileSessionInterface,
    "directory": "sessions",  # Directory to store session files
    "prefix": "session_"      # Prefix for session files
}
```

**Pros**:

* Unlimited session data size
* Sessions can be invalidated server-side
* Simple setup for single-server environments

**Cons**:

* Not suitable for distributed environments
* Requires filesystem access
* Needs cleanup of expired session files

#### Building Custom Session Backends

You can create custom session backends by implementing the `BaseSessionInterface`:

```python
from nexios.session.base import BaseSessionInterface

class RedisSessionInterface(BaseSessionInterface):
    """Redis-backed session interface"""
    
    def __init__(self, session_key=None):
        super().__init__(session_key)
        self.redis_client = redis.Redis()
    
    async def load(self):
        """Load the session data from Redis"""
        if not self.session_key:
            return
        
        data = self.redis_client.get(f"session:{self.session_key}")
        if data:
            self._data = json.loads(data)
    
    async def save(self):
        """Save the session data to Redis"""
        if not self.session_key:
            self.session_key = self.generate_sid()
        
        expiry = self.get_expiry_age()
        self.redis_client.setex(
            f"session:{self.session_key}",
            expiry,
            json.dumps(self._data)
        )
        self.modified = False
    
    def get_session_key(self):
        """Return the session key"""
        return self.session_key
```

### Session Security Best Practices

Session management requires careful attention to security:

#### 1. Generate a Strong Secret Key

```python
import secrets

# Generate a secure random key
app.config.secret_key = secrets.token_hex(32)

# For production, store this in environment variables
app.config.secret_key = os.environ.get("SECRET_KEY")
```

#### 2. Enable Secure Cookies

```python
app.config.session = {
    "cookie_secure": True,      # Only send cookies over HTTPS
    "cookie_httponly": True,    # Prevent JavaScript access
    "cookie_samesite": "lax"    # Mitigate CSRF attacks
}
```

#### 3. Use Appropriate Session Expiration

```python
# Short expiration for sensitive operations
@app.post("/banking/transfer")
async def transfer(req, res):
    # Verify authentication is recent
    auth_time = req.session.get("auth_time", 0)
    if time.time() - auth_time > 300:  # 5 minutes
        return res.redirect("/re-authenticate")
    
    # Process transfer...
```

#### 4. Regenerate Session IDs for Privilege Changes

```python
@app.post("/login")
async def login(req, res):
    # Authenticate user...
    
    # Regenerate session ID to prevent session fixation
    old_session = dict(req.session)
    req.session.regenerate()
    req.session.update(old_session)
    
    req.session["user_id"] = user.id
    req.session["auth_time"] = time.time()
    
    return res.redirect("/dashboard")
```

#### 5. Implement Session Invalidation

```python
@app.post("/logout")
async def logout(req, res):
    # Clear session and remove cookie
    req.session.clear()
    
    return res.redirect("/login")
```

### Practical Examples

#### Example 1: User Authentication Flow

```python
@app.post("/login")
async def login(req, res):
    data = await req.form
    username = data.get("username")
    password = data.get("password")
    
    # Authenticate user (pseudo-code)
    user = authenticate_user(username, password)
    if not user:
        return res.redirect("/login?error=invalid_credentials")
    
    # Store user info in session
    req.session["user_id"] = user.id
    req.session["username"] = user.username
    req.session["auth_time"] = time.time()
    req.session["is_admin"] = user.is_admin
    
    # Set session to expire in 2 hours
    req.session.set_expiry(7200)
    
    return res.redirect("/dashboard")

@app.get("/dashboard")
async def dashboard(req, res):
    # Check if user is logged in
    if "user_id" not in req.session:
        return res.redirect("/login")
    
    username = req.session["username"]
    return res.html(f"<h1>Welcome, {username}!</h1>")

@app.post("/logout")
async def logout(req, res):
    req.session.clear()
    return res.redirect("/login?message=logged_out")
```

#### Example 2: Shopping Cart

```python
@app.get("/cart")
async def view_cart(req, res):
    # Initialize cart if it doesn't exist
    cart = req.session.get("cart", {})
    
    # Calculate total
    total = sum(item["price"] * item["quantity"] for item in cart.values())
    
    return res.json({
        "items": cart,
        "total": total
    })

@app.post("/cart/add/{product_id}")
async def add_to_cart(req, res):
    product_id = req.path_params.product_id
    quantity = int(req.query_params.get("quantity", 1))
    
    # Get product details (pseudo-code)
    product = get_product(product_id)
    if not product:
        return res.json({"error": "Product not found"}, status_code=404)
    
    # Get or initialize cart
    cart = req.session.get("cart", {})
    
    # Add or update product in cart
    if product_id in cart:
        cart[product_id]["quantity"] += quantity
    else:
        cart[product_id] = {
            "name": product.name,
            "price": product.price,
            "quantity": quantity
        }
    
    # Save cart to session
    req.session["cart"] = cart
    
    return res.json({"success": True, "cart": cart})

@app.post("/cart/clear")
async def clear_cart(req, res):
    if "cart" in req.session:
        del req.session["cart"]
    
    return res.json({"success": True})
```

#### Example 3: Multi-step Form with Session Data

```python
@app.get("/wizard/step1")
async def wizard_step1(req, res):
    # Initialize or get form data
    form_data = req.session.get("wizard_data", {})
    
    return res.html_template("wizard/step1.html", form_data=form_data)

@app.post("/wizard/step1")
async def wizard_step1_post(req, res):
    form_data = await req.form
    
    # Validate form (pseudo-code)
    if not validate_step1(form_data):
        return res.redirect("/wizard/step1?error=invalid_data")
    
    # Initialize wizard data if not exists
    wizard_data = req.session.get("wizard_data", {})
    
    # Update with step 1 data
    wizard_data.update({
        "name": form_data.get("name"),
        "email": form_data.get("email")
    })
    
    # Save back to session
    req.session["wizard_data"] = wizard_data
    
    # Proceed to next step
    return res.redirect("/wizard/step2")

@app.post("/wizard/complete")
async def wizard_complete(req, res):
    # Get all wizard data
    wizard_data = req.session.get("wizard_data", {})
    
    # Process the complete submission
    result = process_wizard_submission(wizard_data)
    
    # Clear wizard data from session
    del req.session["wizard_data"]
    
    return res.redirect(f"/wizard/success?id={result.id}")
```

### Troubleshooting

#### Common Issues and Solutions

1. **Sessions not persisting across requests**:
   * Ensure `secret_key` is properly set
   * Check that SessionMiddleware is added to the application
   * Verify browser accepts cookies
2. **Session data size limits**:
   * Cookie-based sessions are limited to \~4KB
   * Switch to a server-side backend for larger data
3. **Session security concerns**:
   * Always use HTTPS in production (`cookie_secure=True`)
   * Set `cookie_httponly=True` to prevent JavaScript access
   * Use appropriate `cookie_samesite` setting
4. **Performance optimization**:
   * Only store necessary data in sessions
   * Consider using Redis or another in-memory store for high-traffic sites

### Conclusion

Nexios provides a flexible, secure session management system that adapts to your application's needs. From simple signed cookies to custom Redis or database backends, you can choose the approach that balances security, performance, and convenience for your specific use case.

***

### icon: server

## Session

Session management is crucial for maintaining user state across requests in a web application. Nexios provides a flexible and scalable approach to session handling, supporting various backends such as in-memory storage, databases, and distributed caches.

#### Basic Configuration

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

#### More Session configuration

```py

app_config = MakeConfig({
    "secret_key" : "super-secure",
    "session":{
        #more session configuration
    }
})


```

#### Session Configuration Table

| Configuration                  | Description                                                                                   |
| ------------------------------ | --------------------------------------------------------------------------------------------- |
| `session_cookie_name`          | The name of the session cookie. Defaults to `"session_id"` if not set.                        |
| `session_cookie_domain`        | The domain for which the session cookie is valid.                                             |
| `session_cookie_path`          | The path for which the session cookie is valid.                                               |
| `session_cookie_httponly`      | Determines if the session cookie should be HTTPOnly, preventing JavaScript access.            |
| `session_cookie_secure`        | Specifies if the session cookie should be transmitted only over HTTPS.                        |
| `session_cookie_samesite`      | Defines the SameSite policy (`None`, `Lax`, or `Strict`). Helps prevent CSRF attacks.         |
| `session_cookie_partitioned`   | Indicates if the cookie should be partitioned for improved security in cross-site contexts.   |
| `session_expiration_time`      | Determines how long the session lasts before expiration. Defaults to `86400` minutes (1 day). |
| `session_permanent`            | If `True`, the session remains active across browser restarts.                                |
| `session_refresh_each_request` | If `True`, resets the session expiration time on every request.                               |

#### Full Example of Session Management in Nexios

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

***

#### Custom manager

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

**Steps to Implement:**

* Inherit from BaseSessionInterface.
* Use an in-memory dictionary (\_session\_store) to hold session data.
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

#### Using the Custom Session Manager

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
