---
icon: shield
---

# CSRF Protection

Cross-Site Request Forgery (CSRF) is a type of attack that forces authenticated users to submit unwanted requests to web applications. Nexios provides robust CSRF protection through its built-in middleware system, allowing you to protect your application from these types of attacks.

## Understanding CSRF

CSRF attacks work by tricking users who are authenticated to your application into executing unwanted actions. For example, if a user is logged into your banking application and visits a malicious website, that website could try to make a request to transfer funds from the user's account without their knowledge.

Nexios CSRF protection works by:

1. Generating a secure token for each user session
2. Requiring that token to be included in non-safe HTTP requests (any method other than GET, HEAD, OPTIONS, or TRACE)
3. Validating the token before processing the request

## Enabling CSRF Protection

To enable CSRF protection in your Nexios application, you need to configure the CSRFMiddleware:

```python
from nexios import get_application
from nexios.middlewares.csrf import CSRFMiddleware

app = get_application()

# Configure the application with a secret key (required for CSRF)
app.config.secret_key = "your-secure-secret-key"
app.config.csrf_enabled = True

# Add the CSRF middleware to your application
app.add_middleware(CSRFMiddleware())
```

## Configuration Options

Nexios offers extensive configuration options for CSRF protection that can be set in your application config:

| Option | Description | Default Value |
|--------|-------------|---------------|
| `csrf_enabled` | Enable/disable CSRF protection | `False` |
| `csrf_required_urls` | List of URL patterns that require CSRF protection | `[]` |
| `csrf_exempt_urls` | List of URL patterns exempt from CSRF protection | `None` |
| `csrf_sensitive_cookies` | List of cookie names that trigger CSRF validation when present | `None` |
| `csrf_safe_methods` | HTTP methods that don't require CSRF validation | `["GET", "HEAD", "OPTIONS", "TRACE"]` |
| `csrf_cookie_name` | Name of the CSRF cookie | `"csrftoken"` |
| `csrf_cookie_path` | Path for the CSRF cookie | `"/"` |
| `csrf_cookie_domain` | Domain for the CSRF cookie | `None` |
| `csrf_cookie_secure` | Whether the cookie should only be sent over HTTPS | `False` |
| `csrf_cookie_httponly` | Whether the cookie should be inaccessible to JavaScript | `True` |
| `csrf_cookie_samesite` | SameSite attribute for the cookie | `"lax"` |
| `csrf_header_name` | Name of the header that should contain the CSRF token | `"X-CSRFToken"` |

### Example Configuration

```python
# Full CSRF configuration example
app.config.csrf_enabled = True
app.config.csrf_required_urls = [r"/api/.*"]  # Regex pattern for all API routes
app.config.csrf_exempt_urls = [r"/public/.*"]  # Exempt public routes
app.config.csrf_sensitive_cookies = ["session", "auth_token"]
app.config.csrf_cookie_secure = True  # Only send over HTTPS
app.config.csrf_cookie_samesite = "strict"  # Strict SameSite policy
```

## Using CSRF Tokens in Forms

When using CSRF protection with HTML forms, you need to include the CSRF token as a hidden field:

```html
<form method="post" action="/api/submit">
    <input type="hidden" name="csrftoken" value="{{ request.cookies.get('csrftoken') }}">
    <!-- Other form fields -->
    <button type="submit">Submit</button>
</form>
```

## Using CSRF Tokens in AJAX Requests

For AJAX requests, you need to include the CSRF token in the headers:

```javascript
// JavaScript example using fetch API
fetch('/api/data', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.cookie.split('; ')
            .find(row => row.startsWith('csrftoken='))
            .split('=')[1]
    },
    body: JSON.stringify({
        // request data
    })
})
```

## CSRF with Single Page Applications (SPAs)

For single-page applications, you'll typically need to retrieve the CSRF token and include it in all non-safe HTTP requests:

```python
# Backend route to get CSRF token
@app.get("/api/csrf-token")
async def get_csrf_token(req, res):
    # The token is automatically set in cookies by the middleware
    # Just return a confirmation
    return res.json({"message": "CSRF token set in cookies"})
```

```javascript
// In your SPA, fetch the token when the app initializes
async function initializeCSRF() {
    await fetch('/api/csrf-token');
    // Now the CSRF token is in cookies and can be used for future requests
}
```

## Security Best Practices

1. **Always enable CSRF protection** for production applications that handle user authentication or sensitive operations.
  
2. **Use HTTPS exclusively** with `csrf_cookie_secure=True` to prevent token theft through network eavesdropping.

3. **Set proper URL patterns**:
   - Use `csrf_required_urls` to explicitly define which URLs need protection
   - Be cautious with `csrf_exempt_urls` - only exempt public or read-only endpoints

4. **Configure strict SameSite policy**:
   - Use `csrf_cookie_samesite="strict"` for high-security applications
   - At minimum, keep the default `"lax"` setting

5. **Make the CSRF token HttpOnly** with `csrf_cookie_httponly=True` to prevent access by JavaScript (except for SPAs that need it)

6. **Customize cookie and header names** in security-critical applications to make them less predictable

7. **Pair CSRF protection with proper Content Security Policy** (CSP) headers for enhanced security

## Troubleshooting

### Common Issues

1. **"CSRF token missing from cookies"** - Ensure that your application is properly setting the CSRF cookie, typically on the first GET request.

2. **"CSRF token missing from headers"** - Check that your client code is correctly extracting and sending the token in the appropriate header.

3. **"CSRF token incorrect"** - This could indicate an expired token or a potential attack. Ensure tokens are refreshed properly.

### Debugging CSRF Issues

To debug CSRF issues, you can temporarily add logging to understand the CSRF validation process:

```python
import logging

# Set up a logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("csrf_debugging")

# In your request handler
@app.post("/api/submit")
async def submit_handler(req, res):
    logger.debug(f"CSRF token in cookie: {req.cookies.get('csrftoken')}")
    logger.debug(f"CSRF token in header: {req.headers.get('X-CSRFToken')}")
    # Rest of your handler code
```

## Example: Complete CSRF Setup

Here's a complete example setting up CSRF protection in a Nexios application:

```python
from nexios import get_application
from nexios.middlewares.csrf import CSRFMiddleware
from nexios.http import Request, Response

# Create the application
app = get_application()

# Configure CSRF protection
app.config.secret_key = "secure-random-secret-key"
app.config.csrf_enabled = True
app.config.csrf_required_urls = [r"/api/.*"]
app.config.csrf_cookie_secure = True
app.config.csrf_cookie_samesite = "lax"

# Add the middleware
app.add_middleware(CSRFMiddleware())

# Routes
@app.get("/")
async def index(req: Request, res: Response):
    # A GET request - CSRF token is set in the response
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>CSRF Example</title></head>
    <body>
        <h1>CSRF Protection Example</h1>
        <form method="post" action="/api/submit">
            <input type="hidden" name="csrftoken" id="csrf-token">
            <input type="text" name="data" placeholder="Enter data">
            <button type="submit">Submit</button>
        </form>
        <script>
            // Extract CSRF token from cookies and add to form
            document.getElementById('csrf-token').value = document.cookie
                .split('; ')
                .find(row => row.startsWith('csrftoken='))
                .split('=')[1];
        </script>
    </body>
    </html>
    """
    return res.html(html)

@app.post("/api/submit")
async def submit(req: Request, res: Response):
    # This route is protected by CSRF
    # The middleware will automatically validate the token
    data = await req.form()
    return res.json({"success": True, "received_data": data.get("data")})

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

This setup provides comprehensive CSRF protection for your Nexios application, particularly for routes under the `/api/` path.

