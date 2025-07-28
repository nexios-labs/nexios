# Understanding CSRF Protection in Nexios

## What is CSRF?

Cross-Site Request Forgery (CSRF) is a security vulnerability that tricks users into performing unwanted actions on web applications where they're authenticated. Attackers can force users to execute state-changing requests (like changing passwords, making purchases, or transferring funds) without their knowledge.

## Why CSRF Protection Matters

Imagine this scenario:

1. You're logged into your bank's website
2. You visit a malicious website in another tab
3. That site contains hidden forms or scripts that submit requests to your bank
4. Because you're already authenticated, these requests appear legitimate

Without CSRF protection, these malicious requests could perform harmful actions on your behalf.

## How CSRF Protection Works

Nexios implements the "Synchronizer Token Pattern":

1. **Token Generation**: A unique, secure token is generated when a user visits your site
2. **Token Storage**: Stored in an HTTP-only cookie and server session
3. **Token Validation**: Required for state-changing requests (POST, PUT, DELETE, etc.)
4. **Request Verification**: Server verifies the token matches the session

## Basic Setup

```python
from nexios import NexiosApp, MakeConfig
from nexios.middleware import CSRFMiddleware

config = MakeConfig(
    secret_key="your-secret-key-here",
    csrf_enabled=True,
    csrf_safe_methods=["GET", "HEAD", "OPTIONS"],
    csrf_required_urls=["*"],
    csrf_cookie_name="csrftoken",
    csrf_header_name="X-CSRFToken"
)

app = NexiosApp(config=config)
app.add_middleware(CSRFMiddleware())
```

## Configuration Options

Nexios provides flexible configuration to customize CSRF protection for your application's needs. Here's a detailed breakdown of each option:

### Core Settings

- **`csrf_enabled`** (boolean, default: `False`)

  - Enables or disables CSRF protection globally
  - **Recommended**: `True` in production environments
  - Example: `csrf_enabled=True`

- **`secret_key`** (string, required)
  - Cryptographic key used to sign CSRF tokens
  - **Security Note**: Keep this secret and consistent across application restarts
  - Example: `secret_key="your-secure-key-123"`

### URL Configuration

- **`csrf_required_urls`** (list of strings, default: `[]`)

  - URL patterns that require CSRF protection
  - Supports wildcard `*` for matching multiple URLs
  - Example: `["/api/*", "/admin/*"]`

- **`csrf_exempt_urls`** (list of strings, default: `[]`)
  - URL patterns excluded from CSRF protection
  - Takes precedence over `csrf_required_urls`
  - Example: `["/api/public/*", "/webhooks/stripe"]`

### HTTP Methods

- **`csrf_safe_methods`** (list of strings, default: `["GET", "HEAD", "OPTIONS"]`)
  - HTTP methods that don't require CSRF tokens
  - These should be idempotent and have no side effects
  - Example: `["GET", "HEAD", "OPTIONS", "TRACE"]`

### Cookie Settings

- **`csrf_cookie_name`** (string, default: `"csrftoken"`)

  - Name of the cookie that stores the CSRF token
  - Change this if you need to avoid naming conflicts
  - Example: `csrf_cookie_name="myapp_csrf_token"`

- **`csrf_cookie_secure`** (boolean, default: `False`)

  - When `True`, the cookie is only sent over HTTPS
  - **Security Best Practice**: Set to `True` in production
  - Example: `csrf_cookie_secure=True`

- **`csrf_cookie_httponly`** (boolean, default: `True`)

  - Prevents JavaScript from accessing the cookie
  - **Security Best Practice**: Keep this as `True`
  - Example: `csrf_cookie_httponly=True`

- **`csrf_cookie_samesite`** (string, default: `"lax"`)
  - Controls when cookies are sent with cross-site requests
  - Options: `"lax"` (recommended), `"strict"`, or `"none"`
  - Note: `"none"` requires `secure=True`
  - Example: `csrf_cookie_samesite="lax"`

### Headers and Forms

- **`csrf_header_name`** (string, default: `"X-CSRFToken"`)

  - HTTP header name for sending CSRF tokens in AJAX requests
  - Example: `"X-CSRF-TOKEN"`

- **`csrf_form_field`** (string, default: `"csrf_token"`)
  - Form field name for CSRF tokens in HTML forms
  - Must match your form field names
  - Example: `"_csrf_token"`

## Client-Side Implementation

### 1. HTML Forms

For traditional form submissions, include the CSRF token in a hidden field. The token should be included in every form that performs state-changing operations (POST, PUT, DELETE, etc.).

```html
<!-- Example: User Profile Update Form -->
<form method="post" action="/profile/update">
  <div class="form-group">
    <label for="username">Username</label>
    <input
      type="text"
      id="username"
      name="username"
      value="{{ current_user.username }}"
      required
    />
  </div>

  <div class="form-group">
    <label for="email">Email</label>
    <input
      type="email"
      id="email"
      name="email"
      value="{{ current_user.email }}"
      required
    />
  </div>

  <button type="submit" class="btn btn-primary">Update Profile</button>
</form>
```

### 2. JavaScript (AJAX) Requests

For AJAX requests, you'll need to:

1. Extract the CSRF token from cookies
2. Include it in the request headers
